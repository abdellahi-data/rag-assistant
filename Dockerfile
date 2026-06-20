# base image: slim python, small and standard
FROM python:3.12-slim


# the aws lambda web adapter: lets this normal web app run on lambda unchanged.
# it sits as a lambda extension and forwards invocations to uvicorn over http.
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter
 
# tell the adapter which port our server listens on
ENV AWS_LWA_PORT=8000


# where the app lives inside the container
WORKDIR /app

# install deps first (this layer is cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the application code
COPY src/ ./src/
COPY providers/ ./providers/
COPY vectorstore.py rag.py ingest.py api.py ./

# copy the prebuilt index + source pdfs into the image (self-contained).
COPY data/ ./data/

# the api listens on 8000
EXPOSE 8000

# launch the server. host 0.0.0.0 so it's reachable from outside the container.
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]