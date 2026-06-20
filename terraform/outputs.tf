# the url to call the deployed api
output "function_url" {
  value = aws_lambda_function_url.app.function_url
}
