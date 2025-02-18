import { Box, Flex, Text, Link, IconButton, HStack } from "@chakra-ui/react";
import { FaFacebook, FaTwitter, FaInstagram, FaLinkedin } from "react-icons/fa";

const Footer = () => {
  return (
    <Box bg="gray.800" color="white" py={6} px={4} mt={10}>
      <Flex direction="column" align="center">
        <Text fontSize="lg" fontWeight="bold">Crowdfunding Platform</Text>
        <HStack spacing={4} mt={2}>
          <IconButton as="a" href="#" aria-label="Facebook" icon={<FaFacebook />} />
          <IconButton as="a" href="#" aria-label="Twitter" icon={<FaTwitter />} />
          <IconButton as="a" href="#" aria-label="Instagram" icon={<FaInstagram />} />
          <IconButton as="a" href="#" aria-label="LinkedIn" icon={<FaLinkedin />} />
        </HStack>
        <Text fontSize="sm" mt={3}>&copy; {new Date().getFullYear()} Crowdfunding Platform. All rights reserved.</Text>
      </Flex>
    </Box>
  );
};

export default Footer;
