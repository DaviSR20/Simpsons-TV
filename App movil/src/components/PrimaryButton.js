import React from "react";
import { Pressable, StyleSheet, Text } from "react-native";
import { palette } from "../theme/palette";

export default function PrimaryButton({ label, onPress, tone = "primary", disabled = false }) {
  return (
    <Pressable
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        tone === "secondary" && styles.secondary,
        tone === "danger" && styles.danger,
        pressed && !disabled && styles.pressed,
        disabled && styles.disabled,
      ]}
    >
      <Text
        style={[
          styles.label,
          tone === "secondary" && styles.secondaryLabel,
          tone === "danger" && styles.dangerLabel,
        ]}
      >
        {label}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: 52,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: palette.primary,
    paddingHorizontal: 18,
  },
  secondary: {
    backgroundColor: palette.cardAlt,
    borderWidth: 1,
    borderColor: palette.border,
  },
  danger: {
    backgroundColor: palette.danger,
  },
  pressed: {
    opacity: 0.85,
    transform: [{ scale: 0.99 }],
  },
  disabled: {
    opacity: 0.45,
  },
  label: {
    color: palette.primaryText,
    fontSize: 16,
    fontWeight: "800",
  },
  secondaryLabel: {
    color: palette.text,
  },
  dangerLabel: {
    color: "#fff",
  },
});
