# the function, running our container image from ECR
resource "aws_lambda_function" "app" {
  function_name = var.project_name
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.app.repository_url}:latest"

  timeout     = 60   # seconds; rag + bedrock can take a few seconds, esp. cold
  memory_size = 2048 # MB; faiss + index

  environment {
    variables = {
      LLM_PROVIDER        = "bedrock"
      EMBEDDING_PROVIDER  = "bedrock"
      AWS_LWA_PORT        = "8000"
      BEDROCK_LLM_MODEL   = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
      BEDROCK_EMBED_MODEL = "amazon.titan-embed-text-v2:0"
    }
  }
}

# a public https endpoint for the function (no api gateway needed)
resource "aws_lambda_function_url" "app" {
  function_name      = aws_lambda_function.app.function_name
  authorization_type = "NONE" # public; 
}
