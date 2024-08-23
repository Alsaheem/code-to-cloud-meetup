provider "aws" {
  region = "eu-west-2"
}


module "static-website" {
    source = "./modules/static-website"
    for_each = {for key, val in var.s3_bukets:
    key => val if val.created_status == true}
    bucket_name = each.value.bucket_name
}