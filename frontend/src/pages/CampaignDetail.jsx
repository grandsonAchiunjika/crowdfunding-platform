import { Box, Text, Button } from "@chakra-ui/react";
import Layout from "../components/Layout";

const CampaignDetail = () => {
  return (
    <Layout>
      <Box maxW="800px" mx="auto" py={10} textAlign="center">
        <Text fontSize="3xl" fontWeight="bold">Campaign Title</Text>
        <Text mt={3} fontSize="lg">Campaign description goes here...</Text>
        <Button mt={5} colorScheme="blue">Donate Now</Button>
      </Box>
    </Layout>
  );
};

export default CampaignDetail;
