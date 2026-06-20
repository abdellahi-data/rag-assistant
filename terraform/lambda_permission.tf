# allow public (unauthenticated) callers to invoke the function via its url.
# aws requires BOTH permissions below for new function urls.

resource "aws_lambda_permission" "public_url" {
  statement_id           = "AllowPublicFunctionUrl"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.app.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "public_invoke" {
  statement_id           = "AllowPublicInvoke"
  action                 = "lambda:InvokeFunction"
  function_name          = aws_lambda_function.app.function_name
  principal              = "*"
}