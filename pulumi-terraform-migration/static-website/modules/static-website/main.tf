# Creating an s3 bucket
resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.bucket_name
  tags = {
    Environment = "production"
  }
}

# Creating s3 bucket ownership control
resource "aws_s3_bucket_ownership_controls" "s3_bucket_ownership_control" {
  bucket = aws_s3_bucket.s3_bucket.id
  rule {
    object_ownership = "ObjectWriter"
  }
}

# Creating public access control
resource "aws_s3_bucket_public_access_block" "s3_bucket_access_control" {
  bucket = aws_s3_bucket.s3_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Creating access control list
resource "aws_s3_bucket_acl" "s3_bucket_access_control_list" {
  depends_on = [
    aws_s3_bucket_ownership_controls.s3_bucket_ownership_control,
    aws_s3_bucket_public_access_block.s3_bucket_access_control,
  ]

  bucket = aws_s3_bucket.s3_bucket.id
  acl    = "public-read"
} 

# Creating website configuration
resource "aws_s3_bucket_website_configuration" "static_website" {
  bucket = aws_s3_bucket.s3_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# Creating bucket policy
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.s3_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
     {
      Effect = "Allow"
      Principal = "*"
      Action = [
       "s3:GetObject",
       "s3:PutObject"
      ]
      Resource = [
        "${aws_s3_bucket.s3_bucket.arn}/*",
        aws_s3_bucket.s3_bucket.arn
      ]
      }
   ]
  })
}

locals {
  s3_origin_id = "myS3Origin"
}

resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = "OAI for ${var.bucket_name}"
}

# Creating cloudfront distribution
resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name              = aws_s3_bucket.s3_bucket.bucket_regional_domain_name
    origin_id                = local.s3_origin_id
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  custom_error_response {
        error_caching_min_ttl = 10
        error_code            = 403
        response_code         = 200
        response_page_path    = "/index.html"
        
  }

  custom_error_response  {
        error_caching_min_ttl = 10
        error_code            = 404
        response_code         = 200
        response_page_path    = "/index.html"
  }

  tags = {
    Environment = "production"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
