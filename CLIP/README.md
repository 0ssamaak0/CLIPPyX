# Using MobileCLIP

There's an option to run `CLIPPyX` using Apple's [MobileCLIP](https://github.com/apple/ml-mobileclip/tree/main) which is faster and consumes less memory [more details in paper](https://arxiv.org/pdf/2311.17049)

- Clone MobileCLIP repository in this dir
- follow the installation options

    Note: if you already have `torch`. you can change `torch` version in `ml-mobileclip/requirements.txt` to avoid reinsatlling it again (I tried it in `2.3.0` and it worked!)

- in `config.yaml`, `clip:` set `provider` to `mobileclip`
- change the checkpoint if u want (default is `mobileclip_s0`)