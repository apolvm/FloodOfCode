gcloud builds submit --tag gcr.io/codeflood-331317/ --project=codeflood-331317

gcloud run deploy --image gcr.io/codeflood-331317/ --platform managed --project=codeflood-331317 --allow-unauthenticated
