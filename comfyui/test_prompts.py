#!/usr/bin/env python3
"""
Extended prompt testing for ComfyUI to find optimal patterns for blog images.
Tests different prompt structures and styles.
"""

import json
import urllib.request
import time
import uuid

COMFYUI_URL = "http://localhost:8188"


def create_sdxl_workflow(
 prompt: str,
 negative_prompt: str = "blurry, low quality, distorted, deformed, ugly, bad anatomy, text, watermark, signature",
 width: int = 1024,
 height: int = 1024,
 steps: int = 25,
 cfg: float = 7.0,
 seed: int = None,
):
 """Create a basic SDXL workflow."""
 if seed is None:
 seed = int(time.time * 1000) % (2**32)

 return {
 "3": {
 "class_type": "KSampler",
 "inputs": {
 "cfg": cfg,
 "denoise": 1.0,
 "latent_image": ["5", 0],
 "model": ["4", 0],
 "negative": ["7", 0],
 "positive": ["6", 0],
 "sampler_name": "euler",
 "scheduler": "normal",
 "seed": seed,
 "steps": steps
 }
 },
 "4": {
 "class_type": "CheckpointLoaderSimple",
 "inputs": {"ckpt_name": "dreamshaper_xl.safetensors"}
 },
 "5": {
 "class_type": "EmptyLatentImage",
 "inputs": {"batch_size": 1, "height": height, "width": width}
 },
 "6": {
 "class_type": "CLIPTextEncode",
 "inputs": {"clip": ["4", 1], "text": prompt}
 },
 "7": {
 "class_type": "CLIPTextEncode",
 "inputs": {"clip": ["4", 1], "text": negative_prompt}
 },
 "8": {
 "class_type": "VAEDecode",
 "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
 },
 "9": {
 "class_type": "SaveImage",
 "inputs": {"filename_prefix": "prompt_test", "images": ["8", 0]}
 }
 }


def queue_prompt(workflow: dict) -> str:
 client_id = str(uuid.uuid4)
 data = json.dumps({"prompt": workflow, "client_id": client_id}).encode('utf-8')
 req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
 req.add_header('Content-Type', 'application/json')
 with urllib.request.urlopen(req) as response:
 result = json.loads(response.read)
 return result.get('prompt_id'), client_id


def get_history(prompt_id: str) -> dict:
 with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
 return json.loads(response.read)


def wait_for_completion(prompt_id: str, timeout: int = 120) -> dict:
 start = time.time
 while time.time - start < timeout:
 history = get_history(prompt_id)
 if prompt_id in history:
 return history[prompt_id]
 time.sleep(1)
 raise TimeoutError(f"Prompt {prompt_id} did not complete within {timeout}s")


def run_test(name: str, prompt: str, negative: str = None, seed: int = 42, width: int = 1024, height: int = 1024):
 """Run a single test."""
 print(f"\n--- {name} ---")
 print(f"Prompt: {prompt[:100]}...")

 workflow = create_sdxl_workflow(
 prompt=prompt,
 negative_prompt=negative or "blurry, low quality, distorted, deformed, ugly, bad anatomy, text, watermark",
 seed=seed,
 width=width,
 height=height,
 )

 try:
 prompt_id, _ = queue_prompt(workflow)
 result = wait_for_completion(prompt_id)
 outputs = result.get('outputs', {})
 for node_id, node_output in outputs.items:
 if 'images' in node_output:
 for img in node_output['images']:
 print(f" -> {img['filename']}")
 return True
 except Exception as e:
 print(f" FAILED: {e}")
 return False


# ============================================================================
# PROMPT PATTERN TESTS
# ============================================================================

# Blog hero image dimensions (1.91:1 aspect ratio)
HERO_WIDTH = 1216
HERO_HEIGHT = 640

print("=" * 60)
print("COMFYUI PROMPT PATTERN TESTING")
print("Finding optimal prompts for blog images")
print("=" * 60)

# Test 1: Style keywords comparison
print("\n\n=== TEST GROUP 1: Style Keywords ===")
print("Testing which style keywords produce best results\n")

style_tests = {
 "flat_vector": (
 "flat vector illustration of cloud computing architecture, "
 "servers connected to cloud icons, data flow arrows, "
 "minimalist design, clean lines, solid colors, "
 "blue and teal color palette, white background, "
 "no gradients, simple shapes"
 ),
 "isometric": (
 "isometric 3D illustration of a data center, "
 "server racks and network cables, glowing connection points, "
 "tech illustration style, clean geometric shapes, "
 "blue and purple color scheme, soft shadows"
 ),
 "gradient_abstract": (
 "abstract digital art representing artificial intelligence, "
 "flowing gradient shapes, particle effects, "
 "modern tech aesthetic, purple to blue gradient background, "
 "glowing accents, cinematic lighting"
 ),
 "line_art": (
 "technical line art diagram of machine learning workflow, "
 "input data flowing through neural network layers to output, "
 "blueprint style, clean white lines on dark blue background, "
 "minimal design, no shading"
 ),
 "editorial_photo": (
 "editorial photograph of a modern tech startup office, "
 "diverse team collaborating around whiteboard with diagrams, "
 "natural window lighting, shallow depth of field, "
 "professional business photography, candid moment"
 ),
}

for name, prompt in style_tests.items:
 run_test(f"style_{name}", prompt, width=HERO_WIDTH, height=HERO_HEIGHT)


# Test 2: Negative prompt variations
print("\n\n=== TEST GROUP 2: Negative Prompt Impact ===")

base_prompt = (
 "professional infographic showing data pipeline architecture, "
 "clean modern design, tech illustration, blue color scheme"
)

negative_tests = {
 "minimal_negative": "blurry, low quality",
 "standard_negative": "blurry, low quality, distorted, deformed, text, watermark, signature",
 "detailed_negative": (
 "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
 "text, words, letters, watermark, signature, logo, "
 "photorealistic, photograph, 3d render, grainy, noisy"
 ),
}

for name, neg in negative_tests.items:
 run_test(f"neg_{name}", base_prompt, negative=neg, seed=100, width=HERO_WIDTH, height=HERO_HEIGHT)


# Test 3: CFG scale impact (we'll need to modify the function for this)
print("\n\n=== TEST GROUP 3: Concept-specific prompts ===")
print("Testing prompts for specific blog topics\n")

concept_prompts = {
 "data_engineering": (
 "modern tech illustration of data engineering pipeline, "
 "stylized database icons connected by flowing data streams, "
 "ETL process visualization, clean vector style, "
 "professional infographic aesthetic, teal and orange accents"
 ),
 "machine_learning": (
 "artistic visualization of a neural network learning, "
 "abstract brain made of interconnected nodes and pathways, "
 "glowing synapses, data particles flowing through layers, "
 "dark background with blue and purple bioluminescent glow"
 ),
 "cloud_architecture": (
 "isometric illustration of cloud infrastructure, "
 "stylized servers, containers, and microservices, "
 "kubernetes pods floating in cloud environment, "
 "modern flat design, pastel colors, clean white background"
 ),
 "ai_automation": (
 "conceptual illustration of AI automation in business, "
 "robot arm and human hand working together on digital interface, "
 "holographic displays showing charts and workflows, "
 "futuristic but approachable, warm lighting"
 ),
 "knowledge_graph": (
 "abstract visualization of a knowledge graph, "
 "interconnected nodes representing concepts and relationships, "
 "constellation-like network pattern, "
 "dark space background, glowing cyan connections, "
 "professional data visualization aesthetic"
 ),
}

for name, prompt in concept_prompts.items:
 run_test(f"concept_{name}", prompt, width=HERO_WIDTH, height=HERO_HEIGHT)


print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("Review outputs in comfyui/outputs/")
print("=" * 60)
