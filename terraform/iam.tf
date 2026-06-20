# the role lambda assumes when it runs
resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-lambda-role"

  # who is allowed to assume this role: the lambda service
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# let the function write logs to cloudwatch (aws-managed policy)
resource "aws_iam_role_policy_attachment" "logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# let the function call bedrock models
resource "aws_iam_role_policy" "bedrock" {
  name = "${var.project_name}-bedrock"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["bedrock:InvokeModel"]
      Resource = "*"
    }]
  })
}
