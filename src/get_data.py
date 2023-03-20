import boto3
import botocore
import botocore.config
from pathlib import Path
import os


if __name__ == "__main__":
    # Do some filtering, maybe we don't want to download TB of data.
    accepted_file_extensions = [".json", ".tif"]
    accepted_tasks = ["Panama Canal"]           # "Buenos Aires", "Kourou", etc etc
    accepted_products = ["METADATA", "GEC"]     # Metadata for JSON, GEC for GeoTIFF amplitude data
    s3 = boto3.resource('s3', config=botocore.config.Config(signature_version=botocore.UNSIGNED))
    bucket_name = 'umbra-open-data-catalog'
    bucket_content = s3.Bucket(bucket_name)
    available_files = bucket_content.objects.filter(Prefix="sar-data/tasks/")

    objects_to_download = []
    for obj in available_files:
        crt_key_path = Path(obj.key)
        location_name = crt_key_path.parts[2]
        file_name = crt_key_path.name
        file_ext = crt_key_path.suffix
        if not any([task in location_name for task in accepted_tasks]):
            continue
        if not any([product in file_name for product in accepted_products]):
            continue
        if file_ext not in accepted_file_extensions:
            continue
        objects_to_download.append(obj)

    # # Uncomment for a sample.
    # objects_to_download = objects_to_download[:3]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    base_path = Path("../data/")
    for crt_object in objects_to_download:
        crt_object_key = Path(crt_object.key)
        if (base_path / crt_object_key).exists():
            continue
        file_parent = crt_object_key.parent
        crt_dest_folder = base_path / file_parent
        crt_dest_folder.mkdir(parents=True, exist_ok=True)
        crt_dest_file = crt_dest_folder / crt_object_key.name
        # download the file in the correct location
        print(f"Downloading {crt_object_key} to {crt_dest_file}")
        bucket_content.download_file(crt_object.key, str(crt_dest_file))


