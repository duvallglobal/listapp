import { corsHeaders } from "@shared/cors.ts";

Deno.serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { imageBase64, condition } = await req.json();

    if (!imageBase64) {
      return new Response(JSON.stringify({ error: "Image data is required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    console.log("Starting product analysis...");
    console.log("Condition:", condition);
    console.log("Image size:", imageBase64.length);

    // Get API keys from environment
    const visionApiKey = Deno.env.get("VISION_AI_API_KEY");
    const geminiApiKey = Deno.env.get("GEMINI_API_KEY");

    if (!visionApiKey || !geminiApiKey) {
      console.error("Missing API keys");
      throw new Error("API keys not configured");
    }

    // Extract base64 data (remove data:image/...;base64, prefix if present)
    const base64Data = imageBase64.includes(",")
      ? imageBase64.split(",")[1]
      : imageBase64;

    console.log("Extracted base64 data length:", base64Data.length);

    // Step 1: Use Google Cloud Vision API for image analysis
    let visionLabels: string[] = [];
    let visionTexts: string[] = [];
    let visionObjects: string[] = [];

    try {
      console.log("Calling Google Cloud Vision API...");
      const visionResponse = await fetch(
        `https://vision.googleapis.com/v1/images:annotate?key=${visionApiKey}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            requests: [
              {
                image: {
                  content: base64Data,
                },
                features: [
                  { type: "LABEL_DETECTION", maxResults: 10 },
                  { type: "TEXT_DETECTION", maxResults: 10 },
                  { type: "OBJECT_LOCALIZATION", maxResults: 10 },
                ],
              },
            ],
          }),
        },
      );

      console.log("Vision API response status:", visionResponse.status);

      if (visionResponse.ok) {
        const visionData = await visionResponse.json();
        console.log("Vision API response received");

        // Extract labels
        if (visionData.responses?.[0]?.labelAnnotations) {
          visionLabels = visionData.responses[0].labelAnnotations
            .map((label: any) => label.description)
            .slice(0, 10);
        }

        // Extract text
        if (visionData.responses?.[0]?.textAnnotations) {
          visionTexts = visionData.responses[0].textAnnotations
            .map((text: any) => text.description)
            .slice(0, 5);
        }

        // Extract objects
        if (visionData.responses?.[0]?.localizedObjectAnnotations) {
          visionObjects = visionData.responses[0].localizedObjectAnnotations
            .map((obj: any) => obj.name)
            .slice(0, 10);
        }

        console.log("Vision analysis completed:", {
          labels: visionLabels.length,
          texts: visionTexts.length,
          objects: visionObjects.length,
        });
      } else {
        const errorText = await visionResponse.text();
        console.error(
          `Vision API error: ${visionResponse.status} - ${errorText}`,
        );
      }
    } catch (visionError) {
      console.error("Vision API failed:", visionError);
    }

    // Step 2: Use Google Gemini API for comprehensive analysis
    const analysisPrompt = `You are an expert product appraiser and marketplace analyst. Analyze this product image and provide a comprehensive valuation and marketplace recommendation.

Product Condition: ${condition}

Vision AI detected labels: ${visionLabels.join(", ")}
Vision AI detected objects: ${visionObjects.join(", ")}
Vision AI detected text: ${visionTexts.slice(0, 3).join(", ")}

Based on the image and detected features, provide a detailed analysis in the following JSON format (respond with ONLY the JSON, no additional text):
{
  "productName": "Specific product name based on what you see",
  "brand": "Brand name if identifiable from image or text",
  "category": "Product category (e.g., Electronics, Clothing, Home & Garden, etc.)",
  "material": "Primary material you can identify",
  "color": "Primary color(s) visible",
  "estimatedAge": "Age or era estimate if applicable",
  "keyFeatures": ["feature1", "feature2", "feature3"],
  "condition": "Detailed condition assessment based on visual inspection",
  "pricing": {
    "low": 25,
    "median": 50,
    "high": 85
  },
  "marketplaceRecommendations": [
    {
      "platform": "eBay",
      "suitability": 8,
      "reasoning": "Why this platform is good for this specific item",
      "estimatedProfit": 42.50
    },
    {
      "platform": "Facebook Marketplace",
      "suitability": 6,
      "reasoning": "Platform-specific reasoning",
      "estimatedProfit": 45.00
    },
    {
      "platform": "Poshmark",
      "suitability": 7,
      "reasoning": "Platform-specific reasoning",
      "estimatedProfit": 40.00
    }
  ],
  "generatedTitle": "SEO-optimized listing title with key details",
  "description": "Compelling product description highlighting key features and condition",
  "tags": ["relevant", "search", "keywords", "for", "listing"],
  "confidenceScore": 0.85
}

Base your pricing on current market trends for similar items. Consider the condition, brand recognition, and category demand. Be realistic and conservative in your estimates. For marketplace recommendations, consider fees, audience, and item category fit.`;

    let analysisResult;

    try {
      console.log("Calling Google Gemini API...");
      const geminiResponse = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${geminiApiKey}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  {
                    text: analysisPrompt,
                  },
                  {
                    inline_data: {
                      mime_type: "image/jpeg",
                      data: base64Data,
                    },
                  },
                ],
              },
            ],
            generationConfig: {
              maxOutputTokens: 2048,
              temperature: 0.4,
              topP: 0.8,
            },
          }),
        },
      );

      console.log("Gemini response status:", geminiResponse.status);

      if (!geminiResponse.ok) {
        const errorText = await geminiResponse.text();
        console.error(
          `Gemini API error: ${geminiResponse.status} - ${errorText}`,
        );
        throw new Error(`Gemini API error: ${geminiResponse.status}`);
      }

      const geminiData = await geminiResponse.json();
      console.log("Gemini response received");

      const analysisText =
        geminiData.candidates?.[0]?.content?.parts?.[0]?.text || "";

      if (!analysisText) {
        throw new Error("No analysis generated from Gemini");
      }

      console.log("Parsing Gemini response...");

      // Try to parse the JSON response
      try {
        // Extract JSON from the response (in case there's extra text)
        const jsonMatch = analysisText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          analysisResult = JSON.parse(jsonMatch[0]);
          console.log("Successfully parsed Gemini response");
        } else {
          throw new Error("No valid JSON found in Gemini response");
        }
      } catch (parseError) {
        console.error("Failed to parse Gemini response:", parseError);
        console.log("Raw response:", analysisText);
        throw parseError;
      }
    } catch (geminiError) {
      console.error("Gemini API failed:", geminiError);
      console.log("Using enhanced fallback analysis with Vision data");

      // Enhanced fallback using Vision API data
      const detectedProduct =
        visionLabels.length > 0 ? visionLabels[0] : "Product Item";
      const detectedBrand =
        visionTexts.find(
          (text) =>
            text.length > 2 &&
            text.length < 20 &&
            /^[A-Z][a-zA-Z\s]+$/.test(text),
        ) || "Unknown";

      analysisResult = {
        productName: detectedProduct,
        brand: detectedBrand,
        category: categorizeFromLabels(visionLabels),
        material: extractMaterial(visionLabels),
        color: extractColor(visionLabels),
        estimatedAge: "Unknown",
        keyFeatures: visionLabels.slice(0, 3),
        condition: condition,
        pricing: {
          low: 20,
          median: 40,
          high: 70,
        },
        marketplaceRecommendations: [
          {
            platform: "eBay",
            suitability: 8,
            reasoning:
              "eBay has the largest audience and offers competitive fees. Good for most product categories.",
            estimatedProfit: 34,
          },
          {
            platform: "Facebook Marketplace",
            suitability: 6,
            reasoning:
              "Good for local sales with lower fees, ideal for larger items.",
            estimatedProfit: 38,
          },
          {
            platform: "Mercari",
            suitability: 7,
            reasoning:
              "Easy to use platform with good reach for general merchandise.",
            estimatedProfit: 36,
          },
        ],
        generatedTitle: `${detectedProduct} - ${condition} Condition`,
        description: `This ${detectedProduct.toLowerCase()} is in ${condition} condition. ${visionLabels.length > 0 ? `Features include: ${visionLabels.slice(0, 3).join(", ")}.` : ""} Perfect for resale or personal use.`,
        tags: [...visionLabels.slice(0, 5), condition, "resale", "quality"],
        confidenceScore: visionLabels.length > 0 ? 0.75 : 0.6,
      };
    }

    // Validate and enhance the analysis result
    analysisResult = validateAndEnhanceResult(analysisResult, condition);

    console.log("Analysis completed successfully");

    return new Response(
      JSON.stringify({
        success: true,
        analysis: analysisResult,
        rawVisionData: {
          labels: visionLabels.slice(0, 5),
          detectedText: visionTexts.slice(0, 3),
          objects: visionObjects.slice(0, 5),
        },
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  } catch (error) {
    console.error("Analysis error:", error);
    return new Response(
      JSON.stringify({
        success: false,
        error: "Analysis failed",
        details: error.message,
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  }
});

// Helper functions
function categorizeFromLabels(labels: string[]): string {
  const categoryMap: { [key: string]: string[] } = {
    Electronics: [
      "phone",
      "computer",
      "laptop",
      "tablet",
      "camera",
      "headphones",
      "speaker",
    ],
    "Clothing & Accessories": [
      "clothing",
      "shirt",
      "pants",
      "dress",
      "shoe",
      "bag",
      "watch",
      "jewelry",
    ],
    "Home & Garden": [
      "furniture",
      "chair",
      "table",
      "lamp",
      "vase",
      "plant",
      "tool",
    ],
    "Sports & Outdoors": ["sports", "ball", "equipment", "bike", "fitness"],
    "Books & Media": ["book", "magazine", "cd", "dvd"],
    "Toys & Games": ["toy", "game", "puzzle", "doll"],
  };

  for (const [category, keywords] of Object.entries(categoryMap)) {
    if (
      labels.some((label) =>
        keywords.some((keyword) =>
          label.toLowerCase().includes(keyword.toLowerCase()),
        ),
      )
    ) {
      return category;
    }
  }

  return "General";
}

function extractMaterial(labels: string[]): string {
  const materials = [
    "wood",
    "metal",
    "plastic",
    "glass",
    "fabric",
    "leather",
    "ceramic",
    "paper",
  ];

  for (const label of labels) {
    for (const material of materials) {
      if (label.toLowerCase().includes(material)) {
        return material.charAt(0).toUpperCase() + material.slice(1);
      }
    }
  }

  return "Unknown";
}

function extractColor(labels: string[]): string {
  const colors = [
    "red",
    "blue",
    "green",
    "yellow",
    "black",
    "white",
    "brown",
    "gray",
    "silver",
    "gold",
  ];

  for (const label of labels) {
    for (const color of colors) {
      if (label.toLowerCase().includes(color)) {
        return color.charAt(0).toUpperCase() + color.slice(1);
      }
    }
  }

  return "Multi-color";
}

function validateAndEnhanceResult(result: any, condition: string): any {
  // Ensure all required fields are present
  const validated = {
    productName: result.productName || "Product Item",
    brand: result.brand || "Unknown",
    category: result.category || "General",
    material: result.material || "Unknown",
    color: result.color || "Unknown",
    estimatedAge: result.estimatedAge || "Unknown",
    keyFeatures: Array.isArray(result.keyFeatures)
      ? result.keyFeatures
      : ["Quality item"],
    condition: result.condition || condition,
    pricing: {
      low: Math.max(5, result.pricing?.low || 20),
      median: Math.max(10, result.pricing?.median || 40),
      high: Math.max(15, result.pricing?.high || 70),
    },
    marketplaceRecommendations: Array.isArray(result.marketplaceRecommendations)
      ? result.marketplaceRecommendations.slice(0, 3)
      : [
          {
            platform: "eBay",
            suitability: 8,
            reasoning: "Large audience and competitive fees",
            estimatedProfit: (result.pricing?.median || 40) * 0.85,
          },
        ],
    generatedTitle:
      result.generatedTitle ||
      `${result.productName || "Quality Item"} - ${condition} Condition`,
    description:
      result.description ||
      `This item is in ${condition} condition and ready for resale.`,
    tags: Array.isArray(result.tags)
      ? result.tags.slice(0, 10)
      : ["item", "resale", condition],
    confidenceScore: Math.min(1, Math.max(0.5, result.confidenceScore || 0.7)),
  };

  // Ensure pricing is logical
  if (validated.pricing.median <= validated.pricing.low) {
    validated.pricing.median = validated.pricing.low + 10;
  }
  if (validated.pricing.high <= validated.pricing.median) {
    validated.pricing.high = validated.pricing.median + 15;
  }

  return validated;
}
