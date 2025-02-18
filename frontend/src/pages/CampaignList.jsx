import { Box, Text, SimpleGrid } from "@chakra-ui/react";
import Layout from "../components/Layout";

const CampaignList = () => {
  return (
    <Layout>
      <Box textAlign="center" py={10}>
        <Text fontSize="3xl" fontWeight="bold">Explore Campaigns</Text>
        <Text mt={3} fontSize="lg">Find projects that need your support.</Text>
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} mt={6}>
          {/* Campaign Cards will go here */}
        </SimpleGrid>
      </Box>
    </Layout>
  );
};

export default CampaignList;
