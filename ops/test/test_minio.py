import sys
import boto3
from loguru import logger
from botocore.exceptions import ClientError
import hashlib
import time
import os
import enum
import datetime
import botocore
from typing import Union
from pydantic import validate_arguments
from typeguard import typechecked

class FileStatus(enum.Enum):
    NEW = 0
    UPLOADED = 1
    REJECTED = 2


class TimeUnit(enum.Enum):
    DAYS = 60*60*24
    HOURS = 60*60
    MINUTES = 60
    SECONDS = 1


def current_milli_time():
    return round(time.time() * 1000)


def getExpirationDateFromCurrentTime(expired_duration, time_unit):
    current = current_milli_time()
    # print(current)
    expired_time = current + (expired_duration * time_unit.value * 1000)
    # print(expired_time)

    expired_date = datetime.datetime.fromtimestamp(expired_time/1000)
    return expired_date


@typechecked
class S3Client:
    instance: object = None
    config: Union[dict, None] = None

    def __init__(
        self,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        endpoint_url: str = None
    ):
        try:
            if self._check_exist_instance(aws_access_key_id,
                                          aws_secret_access_key,
                                          endpoint_url):
                logger.info("Using old cache client with the same config")
                self.s3_client = self.instance
                logger.success(f"Initialize s3 successed {endpoint_url}")
            else:
                logger.info("Do not find any cache client with new config"
                            "initializing a new s3 client")
                session = boto3.session.Session()
                self.s3_client = session.client(
                    service_name='s3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    endpoint_url=endpoint_url
                )
                check_valid = self._check_valid()
                if not check_valid[0]:
                    logger.error(f"Invalid s3 client : {check_valid[1]}")
                self.__class__.instance = self.s3_client
                self.__class__.config = {
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                    "endpoint_url": endpoint_url
                }
                logger.success(f"Initialize s3 successed {endpoint_url}")
        except Exception as err:
            logger.info(f"Init s3 client error: {err}")
            raise err

    def _check_exist_instance(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        endpoint_url
    ):
        if not S3Client.instance and not S3Client.config:
            return False
        elif aws_access_key_id != S3Client.config["aws_access_key_id"]:
            return False
        elif aws_secret_access_key != S3Client.config["aws_secret_access_key"]:
            return False
        elif endpoint_url != S3Client.config["endpoint_url"]:
            return False
        return True

    def _check_valid(self):
        try:
            self.s3_client.list_buckets()
            return True, "Valid"
        except Exception as err:
            return False, err

    def get_list_bucket(self):
        list_bucket = [bucket['Name'] for bucket in
                       self.s3_client.list_buckets()["Buckets"]]
        return list_bucket

    def is_bucket_exist(
        self,
        bucket_name
    ):
        return bucket_name in self.get_list_bucket()

    def create_bucket(
        self,
        bucket_name: str = None
    ):
        try:
            if bucket_name in self.get_list_bucket():
                logger.error(f"Bucket {bucket_name} is existed")
                return False
            self.s3_client.create_bucket(Bucket=bucket_name)
            return True
        except Exception as err:
            logger.error(f"Create Bucket {bucket_name} Error: {err}")
            return False

    def upload_file(
        self: str,
        path: str,
        bucket_name: str,
        name: str
    ):
        try:
            self.s3_client.upload_file(path, bucket_name, name)
            return True
        except Exception as err:
            logger.error("Upload file failed. "
                         f"File:{path} - Bucket:{bucket_name} - Name:{name}")
            logger.error(err)
            return False

    def upload_folder(
        self,
        path,
        bucket_name
    ):
        try:
            for p, current_dir, files in os.walk(path):
                for f in files:
                    print(f"Upload {os.path.join(p, f).replace(path, '')}")
                    self.s3_client.upload_file(
                        os.path.join(p, f),
                        bucket_name,
                        os.path.join(p, f).replace(path, "")
                    )
            return True
        except Exception as err:
            logger.error("Upload folder failed. "
                         f"File:{path} - Bucket:{bucket_name} - Folder:{path}")
            logger.error(err)
            return False

    def download_file(
        self,
        bucket_name: str,
        name: str,
        path_store: str
    ):
        try:
            self.s3_client.download_file(bucket_name, name, path_store)
            return True
        except Exception as err:
            logger.error("Download file failed. "
                         f"Bucket:{bucket_name} - Name:{name} - Store:{path_store}")
            logger.error(err)
            return False

    def delete_file(
        self,
        bucket_name: str,
        name: str
    ):
        try:
            logger.info(f"delete file {bucket_name} {name}")
            self.s3_client.delete_object(Bucket=bucket_name, Key=name)
            return True
        except Exception as err:
            logger.error("Delete file failed. "
                         f"Bucket:{bucket_name} - Name:{name}")
            logger.error(err)
            return False

    def get_pre_signed_url(
        self,
        bucket_name: str,
        file_name: str
    ):
        url = self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=(60*60*24),
        )
        return url

    def process_upload_via_s3(
        self,
        file_path: str,
        bucket_name: str,
        file_name: str
    ):
        file_size = os.path.getsize(file_path)
        filename, file_extension = os.path.splitext(file_path)
        file_checksum = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        res = self.upload_file(file_path, bucket_name, file_name)
        url = self.getPreSignedUrl(bucket_name, file_name)
        if res:
            logger.info(f"Susscessfully upload {bucket_name} file {file_name}")
        else:
            logger.info(f"Fail to upload {bucket_name} file {file_name}")

        status = FileStatus.UPLOADED.value

        expired_date = getExpirationDateFromCurrentTime(1, TimeUnit.DAYS)

        s3_file_description = {
            "status": status,
            "bucket_name": bucket_name,
            "file_name": file_name,
            "file_size": file_size,
            "file_extension": file_extension,
            "file_url": url,
            "file_url_expiration_date": expired_date,
            "file_check_sum": file_checksum
        }
        return res, s3_file_description
    def check_path_exist(self, path):
        # example: "s3://vss/pq/ls" split -> ['s3:', '', 'vss', 'pq', 'ls'] -> bucket name = vss
        bucket_name = path.split("/")[2]
        prefix = None
        
        if f"s3://{bucket_name}" in path:
            prefix = path.replace(f"s3://{bucket_name}",'')
        count = self.s3_client.list_objects(Bucket=bucket_name,
                                          Prefix=prefix)
        
        if 'Contents' in count.keys():
            return True
        else:
            return False 
if __name__ == '__main__':
    # try:
    #     s3_client = S3Client(aws_access_key_id=1,
    #                          aws_secret_access_key="admin@123",
    #                          endpoint_url="http://192.168.0.231:9200")
    # except:
    #     pass

    # s3_client = S3Client(aws_access_key_id="admin",
    #                      aws_secret_access_key="admin@123",
    #                      endpoint_url="http://192.168.0.231:9200")

    # list_bucket = s3_client.get_list_bucket()
    # print("List bucket: ", list_bucket)

    s3_client = S3Client(aws_access_key_id="admin",
                         aws_secret_access_key="123456a@",
                         endpoint_url="http://192.168.20.133:9000")
    s3_client.create_bucket("event")
    s3_client.create_bucket("vss")   
    list_bucket = s3_client.get_list_bucket()
    print("List bucket: ", list_bucket)

    # if s3_client.check_path_exist("s3://vss/TEST_PARQUET"):
    #     print("Exist")
    # else:
    #     print("Not Exist")
    #list_bucket = s3_client.get_list_bucket()
    #print("List bucket: ", list_bucket)

    # bucket_name = "datbt5-bucket9"
    # response = s3_client.check_create_bucket(bucket_name)
    # print('response: ', response)

    # response = s3_client.download_file( "datbt5-bucket", "background/LLQ-Sercurity-Camera5a", "/mnt/data/ai_server/ceph/LLQ-Sercurity-Camera5a_download.png")
    # print('response: ', response)

    # response = s3_client.upload_folder("/media/Data/bangpc/nfs_storage/tests3", "test1") #upload file
    # print('response: ', response)

    # print(s3_client.getPreSignedUrl("datbt5-bucket","test.jpg"))

    # s3_client.processUploadViaS3("test.jpg","/home/ai_server/abc.jpg","datbt5-bucket")

