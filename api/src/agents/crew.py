
from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
import json
import logging
from typing import Dict, Any, List
import base64

from ..tools.tools import (
    multi_vision_analysis_tool,
    google_shopping_search_tool,
    price_statistics_tool,
    content_generation_tool,
    product_description_tool,
    tags_keywords_tool,
    platform_comparison_tool,
    platform_recommendation_tool
)
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ProductAnalysisCrew:
    """CrewAI orchestration for product analysis workflow"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create and configure the CrewAI crew with agents and tasks"""
        
        # Define Agents
        vision_analyst = Agent(
            role='Vision Analyst',
            goal='Analyze product images to identify key features, category, condition, and marketable attributes',
            backstory="""You are an expert in computer vision and product identification. 
            You specialize in analyzing product images to extract detailed information about 
            the item including its category, condition, brand, model, features, and any 
            unique selling points. You have extensive knowledge of consumer products 
            across all categories.""",
            tools=[multi_vision_analysis_tool],
            verbose=True,
            allow_delegation=False
        )
        
        market_research_analyst = Agent(
            role='Market Research Analyst',
            goal='Research current market prices, competition, and demand for identified products',
            backstory="""You are a market research expert specializing in e-commerce and 
            online marketplaces. You excel at finding current market prices, analyzing 
            competition, identifying price trends, and understanding market demand. 
            You use multiple data sources to provide comprehensive market insights.""",
            tools=[
                google_shopping_search_tool,
                price_statistics_tool
            ],
            verbose=True,
            allow_delegation=False
        )
        
        platform_recommendation_analyst = Agent(
            role='Platform Recommendation Analyst',
            goal='Determine the most profitable marketplace platform for selling the product',
            backstory="""You are an expert in marketplace economics and platform optimization. 
            You understand the fee structures, audience preferences, and selling dynamics 
            of all major e-commerce platforms. You calculate profit margins and recommend 
            the best platform for maximum profitability while considering product category, 
            target audience, and seller goals.""",
            tools=[
                platform_comparison_tool,
                platform_recommendation_tool
            ],
            verbose=True,
            allow_delegation=False
        )
        
        content_strategist = Agent(
            role='Content Strategist',
            goal='Create compelling product titles, descriptions, and tags optimized for the recommended platform',
            backstory="""You are a content marketing expert specializing in e-commerce 
            product listings. You create compelling, SEO-optimized product titles and 
            descriptions that drive sales. You understand platform-specific best practices 
            and know how to highlight product benefits to appeal to target customers.""",
            tools=[
                content_generation_tool,
                product_description_tool,
                tags_keywords_tool
            ],
            verbose=True,
            allow_delegation=False
        )
        
        # Define Tasks
        vision_analysis_task = Task(
            description="""Analyze the provided product image to identify:
            1. Product category and subcategory
            2. Brand and model (if visible)
            3. Key features and attributes
            4. Condition assessment
            5. Any unique selling points
            6. Estimated size/dimensions if apparent
            
            Provide a detailed analysis that will be used for market research and pricing.""",
            agent=vision_analyst,
            expected_output="Detailed product identification with category, features, and condition"
        )
        
        market_research_task = Task(
            description="""Based on the vision analysis results, research the current market for this product:
            1. Search for similar products to understand pricing
            2. Analyze price statistics (min, max, average, median prices)
            3. Identify market demand and competition level
            4. Note any seasonal trends or factors affecting price
            
            Use the product identification from the vision analysis to create effective search queries.""",
            agent=market_research_analyst,
            expected_output="Comprehensive market analysis with pricing data and competition insights",
            context=[vision_analysis_task]
        )
        
        platform_recommendation_task = Task(
            description="""Determine the most profitable platform for selling this product:
            1. Compare fees across all major platforms
            2. Calculate profit margins for each platform
            3. Consider the product category and target audience
            4. Factor in platform-specific advantages
            5. Recommend the optimal platform with rationale
            
            Use market research data to inform pricing strategy.""",
            agent=platform_recommendation_analyst,
            expected_output="Platform recommendation with profit calculations and rationale",
            context=[vision_analysis_task, market_research_task]
        )
        
        content_creation_task = Task(
            description="""Create optimized content for the recommended platform:
            1. Generate a compelling product title (under 80 characters)
            2. Write a detailed product description highlighting benefits
            3. Create relevant tags and keywords for discoverability
            4. Ensure content is optimized for the recommended platform
            
            Use insights from vision analysis, market research, and platform recommendation.""",
            agent=content_strategist,
            expected_output="Complete content package with title, description, and tags",
            context=[vision_analysis_task, market_research_task, platform_recommendation_task]
        )
        
        # Create Crew
        crew = Crew(
            agents=[vision_analyst, market_research_analyst, platform_recommendation_analyst, content_strategist],
            tasks=[vision_analysis_task, market_research_task, platform_recommendation_task, content_creation_task],
            process=Process.sequential,
            verbose=True
        )
        
        return crew
    
    async def analyze_product_image(self, image_data: bytes, estimated_cost: float = 0.0) -> Dict[str, Any]:
        """
        Run the complete product analysis workflow
        
        Args:
            image_data: Raw image bytes
            estimated_cost: Estimated cost of the item to seller
            
        Returns:
            Complete analysis results in the required schema format
        """
        try:
            # Convert image to base64 for tools
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare inputs for the crew
            inputs = {
                'image_data': image_b64,
                'estimated_cost': estimated_cost
            }
            
            # Execute the crew workflow
            logger.info("Starting CrewAI product analysis workflow")
            result = self.crew.kickoff(inputs=inputs)
            
            # Parse and structure the final output
            structured_output = self._structure_crew_output(result, estimated_cost)
            
            return structured_output
            
        except Exception as e:
            logger.error(f"Error in product analysis workflow: {str(e)}")
            return self._create_error_response(str(e))
    
    def _structure_crew_output(self, crew_result: Any, estimated_cost: float) -> Dict[str, Any]:
        """Structure the crew output into the required schema format"""
        try:
            # Extract results from each task
            # Note: CrewAI returns results differently based on version
            # This is a generalized approach that should work with most versions
            
            results = {}
            if hasattr(crew_result, 'tasks_output'):
                # Newer CrewAI versions
                for i, task_output in enumerate(crew_result.tasks_output):
                    if i == 0:
                        results['vision_analysis'] = str(task_output)
                    elif i == 1:
                        results['market_research'] = str(task_output)
                    elif i == 2:
                        results['platform_recommendation'] = str(task_output)
                    elif i == 3:
                        results['content_creation'] = str(task_output)
            else:
                # Fallback for older versions or different result format
                results['raw_output'] = str(crew_result)
            
            # Parse the structured output using Gemini for final formatting
            formatted_output = self._format_final_output(results, estimated_cost)
            
            return formatted_output
            
        except Exception as e:
            logger.error(f"Error structuring crew output: {str(e)}")
            return self._create_error_response(f"Output structuring failed: {str(e)}")
    
    async def _format_final_output(self, crew_results: Dict[str, Any], estimated_cost: float) -> Dict[str, Any]:
        """Use Gemini to format the final output into the required schema"""
        
        prompt = f"""
        Based on the following analysis results from a product analysis crew, format the output into a structured JSON response.
        
        Crew Results:
        {json.dumps(crew_results, indent=2)}
        
        Estimated Item Cost: ${estimated_cost}
        
        Create a JSON response with this exact structure:
        {{
            "productName": "string - extracted product name",
            "detailedDescription": "string - compelling product description",
            "tagsKeywords": ["array", "of", "relevant", "tags"],
            "recommendedPricing": {{
                "suggestedPrice": number,
                "priceReasoning": "string explaining price recommendation",
                "marketAnalysis": {{
                    "averageMarketPrice": number,
                    "priceRange": {{
                        "min": number,
                        "max": number
                    }},
                    "competitionLevel": "Low|Medium|High"
                }}
            }},
            "platformRecommendation": {{
                "recommendedPlatform": "string - best platform name",
                "expectedFees": number,
                "estimatedProfit": number,
                "profitMargin": "string percentage",
                "reasoning": "string explaining why this platform is best",
                "alternativePlatforms": [
                    {{
                        "platform": "string",
                        "expectedFees": number,
                        "estimatedProfit": number
                    }}
                ]
            }},
            "confidence": number between 0 and 1,
            "analysisTimestamp": "ISO timestamp"
        }}
        
        Important:
        - Extract actual data from the crew results
        - Calculate real profits using: suggestedPrice - estimatedCost - platformFees
        - Use actual platform fee calculations from the results
        - Set confidence based on data quality and completeness
        - Return only valid JSON, no additional text
        """
        
        try:
            formatted_result = await self.gemini_service.generate_content(
                prompt, 
                max_tokens=2000, 
                temperature=0.3
            )
            
            # Parse the JSON response
            import re
            from datetime import datetime
            
            # Extract JSON from response (remove any markdown formatting)
            json_match = re.search(r'\{.*\}', formatted_result, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                output = json.loads(json_str)
                
                # Add timestamp if not present
                if 'analysisTimestamp' not in output:
                    output['analysisTimestamp'] = datetime.utcnow().isoformat()
                
                return output
            else:
                raise ValueError("No valid JSON found in Gemini response")
                
        except Exception as e:
            logger.error(f"Error formatting final output: {str(e)}")
            return self._create_fallback_response(crew_results, estimated_cost)
    
    def _create_fallback_response(self, crew_results: Dict[str, Any], estimated_cost: float) -> Dict[str, Any]:
        """Create a fallback response when formatting fails"""
        from datetime import datetime
        
        return {
            "productName": "Product Analysis",
            "detailedDescription": "Product analysis completed. Please review crew results for details.",
            "tagsKeywords": ["product", "analysis", "marketplace"],
            "recommendedPricing": {
                "suggestedPrice": 50.0,
                "priceReasoning": "Default pricing - manual review recommended",
                "marketAnalysis": {
                    "averageMarketPrice": 50.0,
                    "priceRange": {
                        "min": 25.0,
                        "max": 75.0
                    },
                    "competitionLevel": "Medium"
                }
            },
            "platformRecommendation": {
                "recommendedPlatform": "eBay",
                "expectedFees": 8.0,
                "estimatedProfit": 42.0 - estimated_cost,
                "profitMargin": "84%",
                "reasoning": "Default recommendation - manual review recommended",
                "alternativePlatforms": []
            },
            "confidence": 0.5,
            "analysisTimestamp": datetime.utcnow().isoformat(),
            "rawCrewResults": crew_results
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response in the required format"""
        from datetime import datetime
        
        return {
            "productName": "Analysis Error",
            "detailedDescription": f"Analysis failed: {error_message}",
            "tagsKeywords": ["error"],
            "recommendedPricing": {
                "suggestedPrice": 0.0,
                "priceReasoning": "Analysis failed",
                "marketAnalysis": {
                    "averageMarketPrice": 0.0,
                    "priceRange": {
                        "min": 0.0,
                        "max": 0.0
                    },
                    "competitionLevel": "Unknown"
                }
            },
            "platformRecommendation": {
                "recommendedPlatform": "Unknown",
                "expectedFees": 0.0,
                "estimatedProfit": 0.0,
                "profitMargin": "0%",
                "reasoning": "Analysis failed",
                "alternativePlatforms": []
            },
            "confidence": 0.0,
            "analysisTimestamp": datetime.utcnow().isoformat(),
            "error": error_message
        }

# Global instance for use in API endpoints
product_analysis_crew = ProductAnalysisCrew()
