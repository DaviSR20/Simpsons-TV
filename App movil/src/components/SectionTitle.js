import React from "react";
import { StyleSheet, Text } from "react-native";
import { palette } from "../theme/palette";

export default function SectionTitle({ children }) {
  return <Text style={styles.title}>{children}</Text>;
}

const styles = StyleSheet.create({
  title: {
    color: palette.text,
    fontSize: 22,
    fontWeight: "900",
    marginBottom: 8,
  },
});
