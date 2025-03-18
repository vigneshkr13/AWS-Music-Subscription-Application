//Code adapted from Canvas Week 3:
//        https://rmit.instructure.com/courses/125083/pages/week-4-learning-materials-slash-activities?module_item_id=6033327
package com.amazonaws.tasks;

import java.util.Arrays;

import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.amazonaws.services.dynamodbv2.model.AttributeDefinition;
import com.amazonaws.services.dynamodbv2.model.KeySchemaElement;
import com.amazonaws.services.dynamodbv2.model.KeyType;
import com.amazonaws.services.dynamodbv2.model.ProvisionedThroughput;
import com.amazonaws.services.dynamodbv2.model.ScalarAttributeType;

public class MusicCreateTable {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withRegion(Regions.US_EAST_1)
                .withCredentials(DefaultAWSCredentialsProviderChain.getInstance())
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        String tableName = "Music";

        try {
            System.out.println("Please wait while we create the New Table - Music");
            Table table = dynamoDB.createTable(tableName,
                    Arrays.asList(
                            new KeySchemaElement("artist", KeyType.HASH), // Partition key
                            new KeySchemaElement("title", KeyType.RANGE) // Sort key
                    ),
                    Arrays.asList(
                            new AttributeDefinition("artist", ScalarAttributeType.S),
                            new AttributeDefinition("title", ScalarAttributeType.S)
//                            new AttributeDefinition("year", ScalarAttributeType.N),
//                            new AttributeDefinition("web_url", ScalarAttributeType.S),
//                            new AttributeDefinition("image_url", ScalarAttributeType.S)
                    ),
                    new ProvisionedThroughput(10L, 10L));
            table.waitForActive();
            System.out.println("Success. Table status: " + table.getDescription().getTableStatus());

        } catch (Exception e) {
            System.err.println("Unable to create table: ");
            System.err.println(e.getMessage());
        }

    }
}
