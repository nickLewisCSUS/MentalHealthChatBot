import React, { useState } from 'react';
import { Text, View, StyleSheet, Button, TextInput } from "react-native";
import axios from 'axios';

export default function Index() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const sendMessage = async () => {
    try {
      const res = await axios.post("http://10.0.2.2:8000/chat",{
        user_message: message,
      });

      setResponse(res.data.repsonse);
    } catch (error){
      console.error("Error:", error);
      setResponse("Error communicating with chatbot.")
    }
  };

  return (
   <View style={styles.container}>
    <Text style={styles.text}>Chat with AI</Text>
    <TextInput
      style={styles.input}
      placeholder="Type your message..."
      placeholderTextColor="#aaa"
      value={message}
      onChangeText={setMessage}
      />
      <Button title="Send" onPress={sendMessage} />
      {response ? <Text style={styles.response}>{response}</Text>: null}
      </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#25292e',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  text:{
    color: '#fff',
    fontSize: 20,
    marginBottom: 20,
  },
  input: {
    width:"100%",
    padding: 10,
    borderColor: "#555",
    borderWidth: 1,
    borderRadius: 5,
    color: "#fff",
    marginBottom: 20,
    backgroundColor: "#333"
  },
  response: {
    color: "#0f0",
    marginTop: 20,
    textAlign: "center",
  },
});
