import React from "react";
import { Image, StyleSheet, Text, View } from "react-native";
import { palette } from "../theme/palette";

export default function InfoCard({ title, subtitle, rightText, imageSource }) {
  return (
    <View style={styles.card}>
      {imageSource ? <Image source={imageSource} style={styles.thumbnail} resizeMode="cover" /> : null}
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
  thumbnail: {
    width: 76,
    height: 44,
    borderRadius: 10,
    backgroundColor: "#1b2330",
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
