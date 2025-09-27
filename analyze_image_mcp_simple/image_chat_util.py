import json
import os
import base64
import mimetypes
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

# 画像解析のレスポンス
class ImageAnalysisResponse(BaseModel):
    image_path: str = Field(description="画像ファイルのパス")
    prompt: str = Field(description="画像解析用プロンプト")
    extracted_text: str = Field(default="", description="画像から抽出されたテキスト（なければ空文字）")
    description: str = Field(default="", description="画像の説明（不要なら空文字）")
    prompt_response: str = Field(default="", description="プロンプトへの応答（不要なら空文字）")

# 2枚の画像の解析レスポンス
class ImageAnalysisResponsePair(BaseModel):
    image1_path: str = Field(description="1枚目画像ファイルのパス")
    image1_extracted_text: str = Field(default="", description="1枚目画像から抽出されたテキスト")
    image1_description: str = Field(default="", description="1枚目画像の説明")
    image2_path: str = Field(description="2枚目画像ファイルのパス")
    image2_extracted_text: str = Field(default="", description="2枚目画像から抽出されたテキスト")
    image2_description: str = Field(default="", description="2枚目画像の説明")
    prompt: str = Field(description="画像解析用プロンプト")
    prompt_response: str = Field(default="", description="プロンプトへの応答")

class ImageChatUtil:
    @classmethod
    def __create_client(cls) -> AsyncOpenAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        return AsyncOpenAI(api_key=api_key)

    @classmethod
    def __create_text_content_part(cls, text: str) -> Dict[str, Any]:
        return {
            "type": "text",
            "text": text
        }

    @classmethod
    def __create_image_content_part(cls, image_path: str) -> Dict[str, Any]:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        image_data_b64 = base64.b64encode(image_data).decode('utf-8')
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        image_url = f"data:{mime_type};base64,{image_data_b64}"
        return {
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        }

    @classmethod
    async def __chat(cls, messages: List[Dict[str, Any]]) -> str:
        client = cls.__create_client()
        request_params = {
            "model": os.getenv("OPENAI_COMPLETION_MODEL", "gpt-4.1"),
            "messages": messages
        }
        try:
            response = await client.chat.completions.create(**request_params)
        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}")
        response_message = response.choices[0].message
        if not response_message or not response_message.content:
            raise ValueError("No response from OpenAI API.")
        return response_message.content

    @classmethod
    async def generate_image_analysis_response_async(cls, image_path: str, prompt: str) -> ImageAnalysisResponse:
        """
        画像解析を行う。テキスト抽出、画像説明、プロンプト応答のCompletionOutputを生成して、ImageAnalysisResponseで返す
        """
        if prompt:
            modified_prompt = f"Prompt: {prompt}"
        else:
            modified_prompt = ""
        input_data = f"""
        Extract text from the image, describe the image, and respond to the prompt.
        Please reply in the following JSON format.
        {{
            "extracted_text": "Extracted text (empty string if no text)",
            "description": "Description of the image (empty string if not needed)",
            "prompt_response": "Response to the prompt (empty string if no prompt)"
        }}
        {modified_prompt}
        """
        image_content_part = cls.__create_image_content_part(image_path)
        text_content_part = cls.__create_text_content_part(input_data)
        messages = [
            {"role": "user", "content": [image_content_part, text_content_part]}
        ]
        try:
            response = await cls.__chat(messages)
            response_dict = json.loads(response)
        except Exception as e:
            raise RuntimeError(f"Failed to analyze image: {e}")
        return ImageAnalysisResponse(
            image_path=image_path,
            prompt=prompt,
            extracted_text=response_dict.get("extracted_text", ""),
            description=response_dict.get("description", ""),
            prompt_response=response_dict.get("prompt_response", "")
        )

    @classmethod
    async def generate_image_pair_analysis_response_async(cls, path1: str, path2: str, prompt: str) -> ImageAnalysisResponsePair:
        """
        画像2枚とプロンプトから画像解析を行う。各画像のテキスト抽出、各画像の説明、プロンプト応答のCompletionOutputを生成して、ImageAnalysisResponsePairで返す
        """
        if prompt:
            modified_prompt = f"Prompt: {prompt}"
        else:
            modified_prompt = ""
        input_data = f"""
        Extract text from both images, describe both images, and respond to the prompt.
        Please reply in the following JSON format.
        {{
            "image1": {{
                "extracted_text": "Extracted text from first image (empty string if no text)",
                "description": "Description of first image (empty string if not needed)"
            }},
            "image2": {{
                "extracted_text": "Extracted text from second image (empty string if no text)",
                "description": "Description of second image (empty string if not needed)"
            }},
            "prompt_response": "Response to the prompt (empty string if no prompt)"
        }}
        {modified_prompt}
        """
        image1_content_part = cls.__create_image_content_part(path1)
        image2_content_part = cls.__create_image_content_part(path2)
        text_content_part = cls.__create_text_content_part(input_data)
        messages = [
            {"role": "user", "content": [image1_content_part, image2_content_part, text_content_part]}
        ]
        try:
            response = await cls.__chat(messages)
            response_dict = json.loads(response)
        except Exception as e:
            raise RuntimeError(f"Failed to analyze image pair: {e}")
        image1_dict = response_dict.get("image1", {})
        image2_dict = response_dict.get("image2", {})
        return ImageAnalysisResponsePair(
            image1_path=path1,
            image1_extracted_text=image1_dict.get("extracted_text", ""),
            image1_description=image1_dict.get("description", ""),
            image2_path=path2,
            image2_extracted_text=image2_dict.get("extracted_text", ""),
            image2_description=image2_dict.get("description", ""),
            prompt=prompt,
            prompt_response=response_dict.get("prompt_response", "")
        )
