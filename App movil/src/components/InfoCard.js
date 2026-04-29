import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { palette } from "../theme/palette";

export default function InfoCard({ title, subtitle, rightText }) {
  return (
    <View style={styles.card}>
      <View style={styles.textBlock}>
        <Text style={styles.title}>{title}</Text>
        {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      </View>
      {rightText ? <Text style={styles.rightText}>{rightText}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: palette.card,
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: palette.border,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
  },
  textBlock: {
    flex: 1,
  },
  title: {
    color: palette.text,
    fontSize: 16,
    fontWeight: "800",
  },
  subtitle: {
    color: palette.muted,
    fontSize: 13,
    marginTop: 4,
  },
  rightText: {
    color: palette.accent,
    fontWeight: "800",
  },
});
