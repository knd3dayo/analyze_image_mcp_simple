
import asyncio
from typing import Annotated
from pydantic import Field
from fastmcp import FastMCP
from analyze_image_mcp_simple.image_chat_util import ImageChatUtil, ImageAnalysisResponse, ImageAnalysisResponsePair


mcp = FastMCP("analyze_image_mcp_simple") #type :ignore

        
@mcp.tool
async def analyze_image_mcp(
    image_path: Annotated[str, Field(description="解析する画像ファイルの絶対パス。必ず絶対パスを指定してください。例: /path/to/image.jpg")],
    prompt: Annotated[str, Field(description="画像解析用のプロンプト")]
) -> Annotated[ImageAnalysisResponse, Field(description="画像の解析結果")]:
    """
    指定した画像とプロンプトを用いて画像解析を行い、解析結果を返します。
    """
    response = await ImageChatUtil.generate_image_analysis_response_async(image_path, prompt)
    return response

@mcp.tool()
async def analyze_two_images_mcp(
    image_path1: Annotated[str, Field(description="1枚目の解析対象画像ファイルの絶対パス。。必ず絶対パスを指定してください。例: /path/to/image1.jpg")],
    image_path2: Annotated[str, Field(description="2枚目の解析対象画像ファイルの絶対パス。必ず絶対パスを指定してください。例: /path/to/image2.jpg")],
    prompt: Annotated[str, Field(description="画像解析用のプロンプト")]
) -> Annotated[ImageAnalysisResponsePair, Field(description="2枚の画像の解析結果")]:
    """
    指定した2枚の画像とプロンプトを用いて画像解析を行い、解析結果を返します。
    """
    response = await ImageChatUtil.generate_image_pair_analysis_response_async(image_path1, image_path2, prompt)
    return response

async def main():
    await mcp.run_async()


if __name__ == "__main__":
    asyncio.run(main())
