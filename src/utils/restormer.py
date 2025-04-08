"""Based on the image restoration model from https://github.com/swz30/Restormer.git"""

from runpy import run_path
import torch
import torch.nn.functional as F
from glob import glob
from skimage.util import img_as_ubyte
import matplotlib.pyplot as plt
from natsort import natsorted

import requests
import os
import cv2
import json

import argparse

class ImageRestormer:
    def __init__(self, task:str):
        self.task = task
    
    def get_model(self, root_dir):
        base_url = "https://github.com/swz30/Restormer/releases/download/v1.0/"
        model_urls = {
            'Real_Denoising': 'real_denoising.pth',
            'Single_Image_Defocus_Deblurring': 'single_image_defocus_deblurring.pth',
            'Motion_Deblurring': 'motion_deblurring.pth',
            'Deraining': 'deraining.pth'
        }
        folder_paths = {
            'Real_Denoising': 'Denoising/',
            'Single_Image_Defocus_Deblurring': 'Defocus_Deblurring/',
            'Motion_Deblurring': 'Motion_Deblurring/',
            'Deraining': 'Deraining/'
        }

        if self.task in model_urls:
            url = base_url + model_urls[self.task]
            folder_path = os.path.join(root_dir,'modules','Restormer','models',folder_paths[self.task])
            os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists
            file_path = os.path.join(folder_path, model_urls[self.task])

            # Download the file
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                print(f"Model downloaded and saved to {file_path}")
            else:
                print(f"Failed to download the model. HTTP Status Code: {response.status_code}")
            return file_path
        else:
            print(f"Task '{self.task}' is not recognized.")

    def load_model(self, root_dir):
        # Define default parameters
        parameters = {
            'inp_channels': 3,
            'out_channels': 3,
            'dim': 48,
            'num_blocks': [4, 6, 6, 8],
            'num_refinement_blocks': 4,
            'heads': [1, 2, 4, 8],
            'ffn_expansion_factor': 2.66,
            'bias': False,
            'LayerNorm_type': 'WithBias',
            'dual_pixel_task': False
        }

        # Adjust parameters based on the task
        if self.task == 'Real_Denoising':
            parameters['LayerNorm_type'] = 'BiasFree'

        # Get weights path
        weights_path = self.get_model(root_dir)

        # Load the architecture
        load_arch = run_path(os.path.join(root_dir, 'modules','Restormer','basicsr', 'models', 'archs', 'restormer_arch.py'))
        model = load_arch['Restormer'](**parameters)
        model = model.to('cuda' if torch.cuda.is_available() else 'cpu')
            
        # Load weights
        checkpoint = torch.load(weights_path)
        model.load_state_dict(checkpoint['params'])
        model.eval()

        return model
    
    def run_model(self, model, input_path, output_dir):
        img_multiple_of = 8
        with torch.no_grad():
            if torch.cuda.is_available():
                torch.cuda.ipc_collect()
                torch.cuda.empty_cache()
            img = cv2.cvtColor(cv2.imread(input_path), cv2.COLOR_BGR2RGB)
            input_ = torch.from_numpy(img).float().div(255.).permute(2,0,1).unsqueeze(0).to('cuda' if torch.cuda.is_available() else 'cpu')

            # Pad the input if not_multiple_of 8
            h,w = input_.shape[2], input_.shape[3]
            H,W = ((h+img_multiple_of)//img_multiple_of)*img_multiple_of, ((w+img_multiple_of)//img_multiple_of)*img_multiple_of
            padh = H-h if h%img_multiple_of!=0 else 0
            padw = W-w if w%img_multiple_of!=0 else 0
            input_ = F.pad(input_, (0,padw,0,padh), 'reflect')

            restored = model(input_)
            restored = torch.clamp(restored, 0, 1)

            # Unpad the output
            restored = restored[:,:,:h,:w]
            restored = restored.permute(0, 2, 3, 1).cpu().detach().numpy()
            restored = img_as_ubyte(restored[0])

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            # Save file with task prefix to keep intermediate states distinct
            filename = os.path.split(input_path)[-1]
            out_filename = f"{self.task}_{filename}"
            out_file_path = os.path.join(output_dir,out_filename)
            print(f"Saving output to {out_file_path}")
            cv2.imwrite(out_file_path, cv2.cvtColor(restored, cv2.COLOR_RGB2BGR))
        return out_file_path
    
    
def main(pipeline, input_dir, output_dir):
    """
    pipeline: dict mapping image file paths to a list of tasks that should be applied sequentially.
              e.g. { "/path/to/image1.jpg": ["Deraining", "Motion_Deblurring"] }
    output_root: directory where the final outputs and intermediate files will be saved.
    """
    # Get unique tasks from the pipeline and preload models for each
    unique_tasks = set()
    for tasks in pipeline.values():
        unique_tasks.update(tasks)
    model_cache = {}
    for task in unique_tasks:
        restormer_obj = ImageRestormer(task)
        model = restormer_obj.load_model(input_dir)
        model_cache[task] = (restormer_obj, model)

    # Process each image
    for image, tasks in pipeline.items():
        print(f"Processing {image}")
        image_path = os.path.join(input_dir, image) #image is the relative path from input_dir
        current_input = image_path
        for task in tasks:
            print(f"Applying {task} on {current_input}")
            restormer_obj, model = model_cache[task]
            # Use an output subfolder per image to keep intermediate outputs organized
            image_output_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(image_path))[0])
            current_input = restormer_obj.run_model(model, current_input, image_output_dir)
    print("Processing completed.")


parser = argparse.ArgumentParser(description='Test Restormer on your own images')
parser.add_argument('--pipeline', type=str, help='dictionary mapping image file paths to a list of tasks that should be applied sequentially')
parser.add_argument('--input_dir', type=str, help='Path to the directory containing your images')
parser.add_argument('--output_dir', type=str, help='Path to the directory where the final outputs will be saved')
if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.pipeline, 'r') as f:
        pipeline = json.load(f)
    main(pipeline, args.input_dir, args.output_dir)