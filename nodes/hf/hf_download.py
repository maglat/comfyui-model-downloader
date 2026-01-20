from ..base_downloader import BaseModelDownloader, get_model_dirs
from ..download_utils import DownloadManager

class HFDownloader(BaseModelDownloader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repo_id": ("STRING", {"multiline": False, "default": "runwayml/stable-diffusion-v1-5"}),
                "filename": ("STRING", {"multiline": False, "default": "v1-5-pruned-emaonly.ckpt"}),
                "local_path": (get_model_dirs(),),
            },
            "optional": {
                "overwrite": ("BOOLEAN", {"default": True}),
                "local_path_override": ("STRING", {"default": ""}),
                "hf_token": ("STRING", {"default": "", "multiline": False, "password": True}),
            },
            "hidden": {"node_id": "UNIQUE_ID"}
        }
    
    FUNCTION = "download"

    def download(self, repo_id, filename, local_path, node_id, overwrite=False, local_path_override="", hf_token=""):
        if not repo_id or not filename:
            print(f"Missing required values: repo_id='{repo_id}', filename='{filename}'")
            return {}
        
        # Wenn ein Token angegeben ist, kurz vorher einloggen
        if hf_token:
            try:
                import huggingface_hub
                huggingface_hub.login(token=hf_token)
            except Exception as e:
                print(f"HF‑Login‑Fehler: {e}")
                raise
        
        final_path = local_path_override if local_path_override else local_path
        
        print(f'downloading model {repo_id} {filename} {final_path} {node_id} {overwrite}')
        self.node_id = node_id
        save_path = self.prepare_download_path(final_path, filename)
        url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
        
        return self.handle_download(
            DownloadManager.download_with_progress,
            save_path=save_path,
            filename=filename,
            overwrite=overwrite,
            url=url,
            progress_callback=self
        )


class HFAuthDownloader(HFDownloader):  # Inherit from HFDownloader to share methods
    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repo_id": ("STRING", {"default": "runwayml/stable-diffusion-v1-5"}),
                "filename": ("STRING", {"default": "v1-5-pruned.ckpt"}),
                "local_path": ("STRING", {"default": "checkpoints"}),
                "hf_token": ("STRING", {"default": "", "multiline": False, "password": True}),
                "overwrite": ("BOOLEAN", {"default": False}),
            }
        }

    # Der Node nutzt das überarbeitete download‑Methoden‑Schema von HFDownloader
    def download_model(self, repo_id, filename, local_path, hf_token, overwrite):
        print(f'downloading model {repo_id} {filename} {local_path} token={"*"*len(hf_token)} overwrite={overwrite}')
        return self.download(
            repo_id=repo_id,
            filename=filename,
            local_path=local_path,
            node_id=self.node_id,
            overwrite=overwrite,
            hf_token=hf_token
        )
