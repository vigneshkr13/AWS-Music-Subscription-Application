//Code adapted from Canvas Week 4:
//        https://rmit.instructure.com/courses/125083/pages/week-4-learning-materials-slash-activities?module_item_id=6033327

package com.amazonaws.tasks;


import java.io.File;
import java.util.Iterator;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class MusicLoadData {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withRegion(Regions.US_EAST_1)
                .withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        Table table = dynamoDB.getTable("Music");

        JsonParser parser = new JsonFactory().createParser(new File("a1.json"));

        JsonNode rootNode = new ObjectMapper().readTree(parser);
        JsonNode songsNode = rootNode.get("songs");

//        ObjectNode currentNode;

        for (JsonNode currentNode : songsNode) {

//            currentNode = (ObjectNode) iter.next();

            String artist = currentNode.path("artist").asText();
            String title = currentNode.path("title").asText();
            int year = currentNode.path("year").asInt();
            String web_url = currentNode.path("web_url").asText();
            String img_url = currentNode.path("img_url").asText();


            try {
                table.putItem(new Item().withPrimaryKey("artist", artist, "title", title)
                        .withInt("year",year)
                        .withString("web_url",web_url)
                        .withString("image_url",img_url));
                System.out.println("PutItem succeeded: " + artist + " " + title + " " + year + " " + web_url + " " +img_url);

            }
            catch (Exception e) {
                System.err.println("Unable to add music: " + artist + " " + title + " " + year + " " + web_url + " " + img_url);
                System.err.println(e.getMessage());
                break;
            }
        }
        parser.close();
    }
}