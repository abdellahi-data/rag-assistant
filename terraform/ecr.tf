# private container registry that will hold the app image
resource "aws_ecr_repository" "app" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true # lets `terraform destroy` remove it even with images inside

  image_scanning_configuration {
    scan_on_push = true
  }
}

# print the repo url after apply (needed to push the image)
output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}
