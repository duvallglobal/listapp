import base64
import io
from typing import Dict, Any, List, Optional
from PIL import Image
import openai
from google.cloud import vision
import os


class VisionService:
    def __init__(self, google_api_key: str, openai_api_key: Optional[str] = None):
        self.google_api_key = google_api_key

        # Initialize Google Vision client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_api_key
        self.vision_client = vision.ImageAnnotatorClient()

        # Initialize OpenAI client
        if openai_api_key:
            openai.api_key = openai_api_key

    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze image using Google Vision API
        """
        try:
            image = vision.Image(content=image_data)

            # Perform multiple types of detection
            response = self.vision_client.annotate_image({
                'image': image,
                'features': [
                    {'type_': vision.Feature.Type.LABEL_DETECTION, 'max_results': 20},
                    {'type_': vision.Feature.Type.TEXT_DETECTION, 'max_results': 10},
                    {'type_': vision.Feature.Type.OBJECT_LOCALIZATION, 'max_results': 10},
                    {'type_': vision.Feature.Type.IMAGE_PROPERTIES}
                ]
            })

            # Process results
            result = {
                "labels": self._process_labels(response.label_annotations),
                "text_annotations": self._process_text(response.text_annotations),
                "objects": self._process_objects(response.localized_object_annotations),
                "image_properties": self._process_image_properties(response.image_properties_annotation)
            }

            # Check for errors
            if response.error.message:
                result["error"] = response.error.message

            return result

        except Exception as e:
            return {"error": f"Google Vision API error: {str(e)}"}

    def analyze_with_gpt4_vision(self, image_base64: str) -> Dict[str, Any]:
        """
        Analyze image using OpenAI GPT-4 Vision
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this product image and provide detailed information in JSON format:
                                {
                                    "product_details": {
                                        "name": "product name",
                                        "brand": "brand name if visible",
                                        "model": "model number if visible",
                                        "category": "product category",
                                        "description": "detailed description",
                                        "features": ["list", "of", "features"],
                                        "color": "primary color",
                                        "materials": ["materials", "if", "visible"]
                                    },
                                    "condition_assessment": {
                                        "score": "condition score 1-10",
                                        "issues": ["any", "visible", "issues"],
                                        "notes": "condition notes"
                                    },
                                    "confidence": "confidence score 0-1"
                                }"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            # Parse the response
            content = response.choices[0].message.content

            # Try to extract JSON from the response
            import json
            import re

            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse GPT-4 Vision response", "raw_response": content}

        except Exception as e:
            return {"error": f"GPT-4 Vision API error: {str(e)}"}

    def _process_labels(self, label_annotations) -> List[Dict[str, Any]]:
        """Process Google Vision label annotations"""
        labels = []
        for label in label_annotations:
            labels.append({
                "description": label.description,
                "score": label.score,
                "topicality": label.topicality
            })
        return labels

    def _process_text(self, text_annotations) -> List[Dict[str, Any]]:
        """Process Google Vision text annotations"""
        texts = []
        for text in text_annotations:
            texts.append({
                "description": text.description,
                "bounding_poly": {
                    "vertices": [
                        {"x": vertex.x, "y": vertex.y}
                        for vertex in text.bounding_poly.vertices
                    ]
                }
            })
        return texts

    def _process_objects(self, object_annotations) -> List[Dict[str, Any]]:
        """Process Google Vision object annotations"""
        objects = []
        for obj in object_annotations:
            objects.append({
                "name": obj.name,
                "score": obj.score,
                "bounding_poly": {
                    "normalized_vertices": [
                        {"x": vertex.x, "y": vertex.y}
                        for vertex in obj.bounding_poly.normalized_vertices
                    ]
                }
            })
        return objects

    def _process_image_properties(self, image_properties) -> Dict[str, Any]:
        """Process Google Vision image properties"""
        if not image_properties:
            return {}

        dominant_colors = []
        if image_properties.dominant_colors:
            for color in image_properties.dominant_colors.colors:
                dominant_colors.append({
                    "color": {
                        "red": color.color.red,
                        "green": color.color.green,
                        "blue": color.color.blue
                    },
                    "score": color.score,
                    "pixel_fraction": color.pixel_fraction
                })

        return {
            "dominant_colors": dominant_colors
        }

    def validate_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Validate image quality and format
        """
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))

            # Get image info
            width, height = image.size
            format = image.format
            mode = image.mode

            # Calculate quality score
            quality_score = 10.0
            issues = []

            # Check resolution
            if width < 800 or height < 600:
                quality_score -= 2.0
                issues.append("Low resolution - consider higher quality image")

            # Check aspect ratio for marketplaces
            aspect_ratio = width / height
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                quality_score -= 1.0
                issues.append("Unusual aspect ratio - square images work best")

            # Check file size
            file_size = len(image_data)
            if file_size > 10 * 1024 * 1024:  # 10MB
                quality_score -= 1.0
                issues.append("Large file size - consider compressing")
            elif file_size < 100 * 1024:  # 100KB
                quality_score -= 1.5
                issues.append("Very small file size - may indicate low quality")

            return {
                "valid": True,
                "width": width,
                "height": height,
                "format": format,
                "mode": mode,
                "file_size": file_size,
                "quality_score": max(0.0, quality_score),
                "issues": issues
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Image validation failed: {str(e)}"
            }

    def optimize_image_for_marketplace(self, image_data: bytes, target_size: tuple = (1200, 1200)) -> bytes:
        """
        Optimize image for marketplace listing
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            # Resize while maintaining aspect ratio
            image.thumbnail(target_size, Image.Resampling.LANCZOS)

            # Save optimized image
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)

            return output.getvalue()

        except Exception as e:
            raise Exception(f"Image optimization failed: {str(e)}")