import { Box, Text, Button, Input, Textarea } from "@chakra-ui/react";
import Layout from "../components/Layout";

const CreateCampaign = () => {
  return (
    <Layout>
      <Box maxW="600px" mx="auto" py={10}>
        <Text fontSize="3xl" fontWeight="bold">Start a Campaign</Text>
        <Input placeholder="Campaign Title" mt={4} />
        <Textarea placeholder="Describe your campaign" mt={4} />
        <Button mt={5} colorScheme="blue">Create Campaign</Button>
      </Box>
    </Layout>
  );
};

export default CreateCampaign;
