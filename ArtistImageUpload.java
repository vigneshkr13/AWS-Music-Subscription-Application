
//Code adapted from Canvas Week 4:
//        https://rmit.instructure.com/courses/125083/pages/week-4-learning-materials-slash-activities?module_item_id=6033327


package com.amazonaws.tasks;


import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.URL;
import java.util.Iterator;

import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ArtistImageUpload {

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode rootNode = mapper.readTree(new File("a1.json"));
        JsonNode songsNode = rootNode.get("songs");

        if (songsNode != null && songsNode.isArray()) {
            for (JsonNode songNode : songsNode) {
                String img_url = songNode.path("img_url").asText();
                downloadAndUploadToS3(img_url);
            }
        } else {
            System.err.println("JSON structure does not contain a 'songs' array.");
        }
    }

    public static void downloadAndUploadToS3(String imageUrl) {
        try {
            URL url = new URL(imageUrl);
            String fileName = imageUrl.substring(imageUrl.lastIndexOf('/') + 1);
            String bucketName = "s3853674-music";
            String s3Key = "images/" + fileName;

            InputStream inputStream = url.openStream();
            File tempFile = File.createTempFile("temp-image-", ".tmp");
            FileOutputStream outputStream = new FileOutputStream(tempFile);

            byte[] buffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }

            inputStream.close();
            outputStream.close();

            AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
                    .withRegion(Regions.US_EAST_1)
                    .withCredentials(DefaultAWSCredentialsProviderChain.getInstance())
                    .build();

            s3Client.putObject(bucketName, s3Key, tempFile);

            System.out.println("Uploaded image to S3: " + s3Key);

            tempFile.delete(); // Clean up temp file

        } catch (Exception e) {
            System.err.println("Error downloading or uploading image: " + imageUrl);
            System.err.println(e.getMessage());
        }
    }
}
