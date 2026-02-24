#!/usr/bin/env python3
"""
Simple image generator for blog posts.
Uses predefined style templates to make generation easy.

Usage:
 python generate.py "topic" --style flat_vector
 python generate.py "topic" --style gradient_abstract --seed 42
 python generate.py --prompt "full custom prompt"
"""

import argparse
import json
import urllib.request
import time
import uuid
import sys
from pathlib import Path

COMFYUI_URL = "http://localhost:8188"

# Style templates - just fill in the topic
STYLES = {
 "flat_vector": {
 "template": (
 "flat vector illustration of {topic}, "
 "minimalist design, clean lines, solid colors, "
 "blue and teal color palette, white background, "
 "no gradients, simple shapes, professional infographic"
 ),
 "negative": "blurry, low quality, distorted, photorealistic, photograph, 3d render, text",
 },
 "isometric": {
 "template": (
 "isometric 3D illustration of {topic}, "
 "tech illustration style, clean geometric shapes, "
 "blue and purple color scheme, soft shadows, "
 "modern design, professional"
 ),
 "negative": "blurry, low quality, distorted, flat, 2d, text, watermark",
 },
 "gradient_abstract": {
 "template": (
 "abstract digital art representing {topic}, "
 "flowing gradient shapes, particle effects, "
 "modern tech aesthetic, purple to blue gradient background, "
 "glowing accents, cinematic lighting"
 ),
 "negative": "blurry, low quality, distorted, text, watermark, ugly",
 },
 "neural": {
 "template": (
 "artistic visualization of {topic}, "
 "abstract brain made of interconnected nodes and pathways, "
 "glowing synapses, data particles flowing through layers, "
 "dark background with blue and purple bioluminescent glow"
 ),
 "negative": "blurry, low quality, distorted, text, watermark, bright background",
 },
 "editorial": {
 "template": (
 "editorial photograph of {topic}, "
 "natural window lighting, shallow depth of field, "
 "professional business photography, candid moment, "
 "modern office environment"
 ),
 "negative": "blurry, low quality, distorted, cartoon, illustration, text",
 },
 "knowledge_graph": {
 "template": (
 "abstract visualization of {topic}, "
 "interconnected nodes representing concepts and relationships, "
 "constellation-like network pattern, "
 "dark space background, glowing cyan connections, "
 "professional data visualization aesthetic"
 ),
 "negative": "blurry, low quality, distorted, text, labels, watermark",
 },
 "data_pipeline": {
 "template": (
 "modern tech illustration of {topic}, "
 "stylized database icons connected by flowing data streams, "
 "ETL process visualization, clean vector style, "
 "professional infographic aesthetic, teal and orange accents"
 ),
 "negative": "blurry, low quality, distorted, photorealistic, text, watermark",
 },
}


def create_workflow(prompt: str, negative: str, width: int, height: int, seed: int, steps: int, cfg: float):
 """Create SDXL workflow."""
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
 "inputs": {"clip": ["4", 1], "text": negative}
 },
 "8": {
 "class_type": "VAEDecode",
 "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
 },
 "9": {
 "class_type": "SaveImage",
 "inputs": {"filename_prefix": "blog", "images": ["8", 0]}
 }
 }


def queue_prompt(workflow: dict) -> str:
 """Queue a workflow and return the prompt_id."""
 client_id = str(uuid.uuid4)
 data = json.dumps({"prompt": workflow, "client_id": client_id}).encode('utf-8')
 req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
 req.add_header('Content-Type', 'application/json')
 with urllib.request.urlopen(req) as response:
 result = json.loads(response.read)
 return result.get('prompt_id')


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
 print(".", end="", flush=True)
 raise TimeoutError(f"Generation did not complete within {timeout}s")


def main:
 parser = argparse.ArgumentParser(description="Generate blog images with ComfyUI")
 parser.add_argument("topic", nargs="?", help="Topic for the image (used with --style)")
 parser.add_argument("--style", "-s", choices=list(STYLES.keys), default="gradient_abstract",
 help="Style template to use")
 parser.add_argument("--prompt", "-p", help="Full custom prompt (ignores topic and style)")
 parser.add_argument("--negative", "-n", help="Custom negative prompt")
 parser.add_argument("--seed", type=int, default=None, help="Random seed (default: random)")
 parser.add_argument("--width", "-W", type=int, default=1216, help="Image width (default: 1216)")
 parser.add_argument("--height", "-H", type=int, default=640, help="Image height (default: 640)")
 parser.add_argument("--steps", type=int, default=25, help="Sampling steps (default: 25)")
 parser.add_argument("--cfg", type=float, default=7.0, help="CFG scale (default: 7.0)")
 parser.add_argument("--list-styles", action="store_true", help="List available styles")

 args = parser.parse_args

 if args.list_styles:
 print("\nAvailable styles:\n")
 for name, style in STYLES.items:
 print(f" {name}:")
 print(f" {style['template'][:80]}...")
 print
 return

 # Build prompt
 if args.prompt:
 prompt = args.prompt
 negative = args.negative or "blurry, low quality, distorted, text, watermark"
 elif args.topic:
 style = STYLES[args.style]
 prompt = style["template"].format(topic=args.topic)
 negative = args.negative or style["negative"]
 else:
 parser.error("Either topic or --prompt is required")

 seed = args.seed if args.seed is not None else int(time.time * 1000) % (2**32)

 print(f"\n{'='*60}")
 print(f"Generating image...")
 print(f"{'='*60}")
 print(f"Style: {args.style}")
 print(f"Prompt: {prompt[:80]}...")
 print(f"Size: {args.width}x{args.height}")
 print(f"Seed: {seed}")
 print(f"{'='*60}\n")

 workflow = create_workflow(
 prompt=prompt,
 negative=negative,
 width=args.width,
 height=args.height,
 seed=seed,
 steps=args.steps,
 cfg=args.cfg,
 )

 try:
 prompt_id = queue_prompt(workflow)
 print(f"Queued: {prompt_id}")
 print("Generating", end="", flush=True)

 result = wait_for_completion(prompt_id)
 print(" Done!\n")

 # Get output filename
 outputs = result.get('outputs', {})
 for node_id, node_output in outputs.items:
 if 'images' in node_output:
 for img in node_output['images']:
 print(f"Generated: comfyui/outputs/{img['filename']}")
 print(f"\nTo copy to post assets:")
 print(f" cp comfyui/outputs/{img['filename']} posts/YOUR-POST/assets/")

 except urllib.error.URLError:
 print("\nError: Cannot connect to ComfyUI.")
 print("Make sure ComfyUI is running: cd comfyui && docker compose up -d")
 sys.exit(1)
 except Exception as e:
 print(f"\nError: {e}")
 sys.exit(1)


if __name__ == "__main__":
 main
