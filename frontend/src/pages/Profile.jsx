import { Box, Text, Button } from "@chakra-ui/react";
import Layout from "../components/Layout";

const Profile = () => {
  return (
    <Layout>
      <Box textAlign="center" py={10}>
        <Text fontSize="3xl" fontWeight="bold">Your Profile</Text>
        <Text mt={3} fontSize="lg">Manage your account and campaigns.</Text>
        <Button mt={5} colorScheme="teal">Edit Profile</Button>
      </Box>
    </Layout>
  );
};

export default Profile;
