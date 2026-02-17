#!/usr/bin/env python3
"""
Test all LoRAs with appropriate prompts to document their styles.
"""

import json
import urllib.request
import time
import uuid

COMFYUI_URL = "http://localhost:8188"

# Hero image dimensions
WIDTH = 1216
HEIGHT = 640

# LoRA test configurations: (lora_file, prompt, strength)
LORA_TESTS = [
    (
        "C64XLv1.safetensors",
        "a C64 desktop computer with 'It's computers!' printed on screen, retro computing, 8-bit aesthetic",
        0.7
    ),
    (
        "DaVinciDrawing01-00a_CE_SDXL_128OT.safetensors",
        "anatomical diagram of a neural network brain, scientific illustration, detailed sketch",
        0.7
    ),
    (
        "HeavyMetalStyle-000009.safetensors",
        "big data planet with SQL spaceship taking off, epic sci-fi scene, dramatic lighting",
        0.8
    ),
    (
        "LineDrawing03_CE_XL_300-OT.safetensors",
        "cloud computing infrastructure diagram, servers and connections, technical illustration",
        0.7
    ),
    (
        "MoviePoster03-02_CE_SDXL_128OT.safetensors",
        "david facing big tech goliath with thousands of agents behind him, epic confrontation, dramatic",
        0.7
    ),
    (
        "Photov3-000008.safetensors",
        "person working at desk with multiple monitors showing code, professional photography, natural lighting",
        0.5
    ),
    (
        "PixelWave_TV.safetensors",
        "machine learning robot assistant, retro futuristic, CRT aesthetic",
        0.7
    ),
    (
        "Retro_80s_Vaporwave.safetensors",
        "futuristic data visualization dashboard, neon colors, synthwave aesthetic",
        0.8
    ),
    (
        "RetroPop01_CE_SDXL.safetensors",
        "knowledge graph connecting ideas, pop art style, bold colors",
        0.7
    ),
    (
        "typographic.safetensors",
        "the word DATA with tech elements, typography design, creative lettering",
        0.8
    ),
    (
        "VintageDrawing01-00_CE_SDXL_128OT.safetensors",
        "old-fashioned diagram of modern cloud architecture, vintage illustration style, engraving",
        0.7
    ),
    (
        "checkpoint-e18_s324.safetensors",
        "abstract representation of artificial intelligence, digital art, futuristic",
        0.6
    ),
]


def create_workflow_with_lora(prompt, negative, lora_name, lora_strength, seed):
    """Create SDXL workflow with LoRA."""
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 7.0,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["10", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "normal",
                "seed": seed,
                "steps": 25
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "dreamshaper_xl.safetensors"}
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": HEIGHT, "width": WIDTH}
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["10", 1], "text": prompt}
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["10", 1], "text": negative}
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"lora_{lora_name.split('.')[0]}", "images": ["8", 0]}
        },
        "10": {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": lora_name,
                "model": ["4", 0],
                "clip": ["4", 1],
                "strength_model": lora_strength,
                "strength_clip": lora_strength
            }
        }
    }


def queue_prompt(workflow):
    client_id = str(uuid.uuid4())
    data = json.dumps({"prompt": workflow, "client_id": client_id}).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        return result.get('prompt_id')


def get_history(prompt_id):
    with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
        return json.loads(response.read())


def wait_for_completion(prompt_id, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        history = get_history(prompt_id)
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(1)
        print(".", end="", flush=True)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def main():
    print("=" * 70)
    print("LORA STYLE TESTING")
    print("=" * 70)

    negative = "blurry, low quality, distorted, deformed, ugly"
    seed = 42  # Fixed seed for comparison

    results = []

    for lora_name, prompt, strength in LORA_TESTS:
        print(f"\n{'─' * 70}")
        print(f"LoRA: {lora_name}")
        print(f"Prompt: {prompt[:60]}...")
        print(f"Strength: {strength}")
        print("─" * 70)

        workflow = create_workflow_with_lora(prompt, negative, lora_name, strength, seed)

        try:
            prompt_id = queue_prompt(workflow)
            print(f"Queued: {prompt_id}")
            print("Generating", end="", flush=True)

            result = wait_for_completion(prompt_id)
            print(" Done!")

            # Get output filename
            outputs = result.get('outputs', {})
            for node_id, node_output in outputs.items():
                if 'images' in node_output:
                    for img in node_output['images']:
                        print(f"Output: {img['filename']}")
                        results.append({
                            "lora": lora_name,
                            "prompt": prompt,
                            "strength": strength,
                            "file": img['filename']
                        })
        except Exception as e:
            print(f" FAILED: {e}")
            results.append({
                "lora": lora_name,
                "prompt": prompt,
                "strength": strength,
                "file": None,
                "error": str(e)
            })

    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
    print("\nResults:")
    for r in results:
        status = r.get('file') or f"ERROR: {r.get('error', 'unknown')}"
        print(f"  {r['lora'][:40]:40} -> {status}")

    print(f"\nImages saved to: comfyui/outputs/")


if __name__ == "__main__":
    main()
