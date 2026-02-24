#!/usr/bin/env python3
"""
Test ComfyUI models and LoRAs to understand what prompts work best.
Generates a grid of test images with different configurations.
"""

import json
import urllib.request
import urllib.parse
import time
import uuid
from pathlib import Path

COMFYUI_URL = "http://localhost:8188"

# Basic SDXL workflow template
def create_sdxl_workflow(
 prompt: str,
 negative_prompt: str = "blurry, low quality, distorted, deformed",
 width: int = 1024,
 height: int = 1024,
 steps: int = 25,
 cfg: float = 7.0,
 seed: int = None,
 lora_name: str = None,
 lora_strength: float = 0.8,
):
 """Create a basic SDXL workflow with optional LoRA."""
 if seed is None:
 seed = int(time.time * 1000) % (2**32)

 workflow = {
 "3": {
 "class_type": "KSampler",
 "inputs": {
 "cfg": cfg,
 "denoise": 1.0,
 "latent_image": ["5", 0],
 "model": ["10", 0] if lora_name else ["4", 0],
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
 "inputs": {
 "ckpt_name": "dreamshaper_xl.safetensors"
 }
 },
 "5": {
 "class_type": "EmptyLatentImage",
 "inputs": {
 "batch_size": 1,
 "height": height,
 "width": width
 }
 },
 "6": {
 "class_type": "CLIPTextEncode",
 "inputs": {
 "clip": ["10", 1] if lora_name else ["4", 1],
 "text": prompt
 }
 },
 "7": {
 "class_type": "CLIPTextEncode",
 "inputs": {
 "clip": ["10", 1] if lora_name else ["4", 1],
 "text": negative_prompt
 }
 },
 "8": {
 "class_type": "VAEDecode",
 "inputs": {
 "samples": ["3", 0],
 "vae": ["4", 2]
 }
 },
 "9": {
 "class_type": "SaveImage",
 "inputs": {
 "filename_prefix": "test",
 "images": ["8", 0]
 }
 }
 }

 # Add LoRA loader if specified
 if lora_name:
 workflow["10"] = {
 "class_type": "LoraLoader",
 "inputs": {
 "lora_name": lora_name,
 "model": ["4", 0],
 "clip": ["4", 1],
 "strength_model": lora_strength,
 "strength_clip": lora_strength
 }
 }

 return workflow


def queue_prompt(workflow: dict) -> str:
 """Queue a workflow and return the prompt_id."""
 client_id = str(uuid.uuid4)
 data = json.dumps({"prompt": workflow, "client_id": client_id}).encode('utf-8')
 req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
 req.add_header('Content-Type', 'application/json')

 with urllib.request.urlopen(req) as response:
 result = json.loads(response.read)
 return result.get('prompt_id'), client_id


def get_history(prompt_id: str) -> dict:
 """Get the history for a specific prompt."""
 with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
 return json.loads(response.read)


def wait_for_completion(prompt_id: str, timeout: int = 120) -> dict:
 """Wait for a prompt to complete."""
 start = time.time
 while time.time - start < timeout:
 history = get_history(prompt_id)
 if prompt_id in history:
 return history[prompt_id]
 time.sleep(1)
 raise TimeoutError(f"Prompt {prompt_id} did not complete within {timeout}s")


def get_available_loras -> list:
 """Get list of available LoRAs."""
 with urllib.request.urlopen(f"{COMFYUI_URL}/object_info/LoraLoader") as response:
 info = json.loads(response.read)
 return info['LoraLoader']['input']['required']['lora_name'][0]


def run_test(name: str, prompt: str, negative: str = None, lora: str = None, lora_strength: float = 0.8):
 """Run a single test and report results."""
 print(f"\n{'='*60}")
 print(f"TEST: {name}")
 print(f"Prompt: {prompt[:80]}...")
 if lora:
 print(f"LoRA: {lora} @ {lora_strength}")
 print(f"{'='*60}")

 workflow = create_sdxl_workflow(
 prompt=prompt,
 negative_prompt=negative or "blurry, low quality, distorted, deformed, ugly, bad anatomy",
 lora_name=lora,
 lora_strength=lora_strength,
 seed=42, # Fixed seed for comparison
 )

 try:
 prompt_id, _ = queue_prompt(workflow)
 print(f"Queued: {prompt_id}")
 result = wait_for_completion(prompt_id)

 # Get output filename
 outputs = result.get('outputs', {})
 for node_id, node_output in outputs.items:
 if 'images' in node_output:
 for img in node_output['images']:
 print(f"Generated: {img['filename']}")

 print("SUCCESS")
 return True
 except Exception as e:
 print(f"FAILED: {e}")
 return False


def main:
 print("ComfyUI Model & LoRA Testing")
 print("="*60)

 # Get available LoRAs
 print("\nAvailable LoRAs:")
 loras = get_available_loras
 for lora in loras:
 print(f" - {lora}")

 # Test prompts for different use cases
 test_prompts = {
 "concept_diagram": (
 "clean vector illustration of a data pipeline, "
 "showing data flowing from sources through processing to storage, "
 "minimal flat design, professional infographic style, "
 "blue and orange color scheme, white background"
 ),
 "tech_illustration": (
 "illustration of an AI brain made of neural network nodes and connections, "
 "glowing blue synapses, digital art style, "
 "clean professional look, dark background"
 ),
 "hero_abstract": (
 "abstract representation of machine learning, "
 "geometric shapes transforming and evolving, "
 "gradient colors from purple to blue, "
 "modern minimalist design, professional"
 ),
 "situational_photo": (
 "professional photograph of a person working at a modern desk, "
 "multiple monitors showing code and data visualizations, "
 "soft natural lighting, shallow depth of field, "
 "editorial photography style"
 ),
 }

 # Test 1: Base model without LoRA
 print("\n" + "="*60)
 print("PHASE 1: Testing Base Model (DreamShaper XL)")
 print("="*60)

 for name, prompt in test_prompts.items:
 run_test(f"base_{name}", prompt)

 # Test 2: Each LoRA with appropriate prompts
 print("\n" + "="*60)
 print("PHASE 2: Testing LoRAs")
 print("="*60)

 lora_tests = [
 ("Flat style-000014.safetensors", "concept_diagram", 0.8),
 ("Minimalist_flat_icons_XL-000006.safetensors", "concept_diagram", 0.7),
 ("CollagePainting XL.safetensors", "hero_abstract", 0.6),
 ("C64XLv1.safetensors", "tech_illustration", 0.5), # Lower for retro effect
 ("MoviePoster03-02_CE_SDXL_128OT.safetensors", "hero_abstract", 0.6),
 ("Beautify-Supermodel-SDXL.safetensors", "situational_photo", 0.4),
 ]

 for lora_name, prompt_key, strength in lora_tests:
 if lora_name in loras:
 run_test(
 f"lora_{lora_name.split('.')[0]}",
 test_prompts[prompt_key],
 lora=lora_name,
 lora_strength=strength
 )
 else:
 print(f"SKIP: {lora_name} not found")

 print("\n" + "="*60)
 print("TESTING COMPLETE")
 print("Check comfyui/outputs/ for generated images")
 print("="*60)


if __name__ == "__main__":
 main
