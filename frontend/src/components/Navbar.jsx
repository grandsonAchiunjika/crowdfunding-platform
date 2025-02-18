import { Box, Flex, Text, HStack, IconButton, Button, useDisclosure, VStack } from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { FaBars, FaTimes } from "react-icons/fa";

const Navbar = () => {
  const { isOpen, onToggle } = useDisclosure();

  return (
    <Box bg="gray.800" color="white" px={6} py={4} boxShadow="md">
      <Flex justify="space-between" align="center">
        {/* Logo */}
        <Text fontSize="2xl" fontWeight="bold">
          <Link to="/">Crowdfunding</Link>
        </Text>

        {/* Desktop Menu */}
        <HStack spacing={6} display={{ base: "none", md: "flex" }}>
          <Link to="/campaigns">Campaigns</Link>
          <Link to="/create">Start a Campaign</Link>
          <Link to="/profile">Profile</Link>
          <Button as={Link} to="/login" colorScheme="blue" size="sm">Login</Button>
          <Button as={Link} to="/register" colorScheme="teal" size="sm">Sign Up</Button>
        </HStack>

        {/* Mobile Menu Button */}
        <IconButton
          icon={isOpen ? <FaTimes /> : <FaBars />}
          display={{ base: "flex", md: "none" }}
          onClick={onToggle}
          aria-label="Toggle Navigation"
        />
      </Flex>

      {/* Mobile Menu */}
      {isOpen && (
        <VStack spacing={4} bg="gray.700" py={4} mt={2} rounded="md" display={{ base: "flex", md: "none" }}>
          <Link to="/campaigns">Campaigns</Link>
          <Link to="/create">Start a Campaign</Link>
          <Link to="/profile">Profile</Link>
          <Button as={Link} to="/login" colorScheme="blue" size="sm">Login</Button>
          <Button as={Link} to="/register" colorScheme="teal" size="sm">Sign Up</Button>
        </VStack>
      )}
    </Box>
  );
};

export default Navbar;
