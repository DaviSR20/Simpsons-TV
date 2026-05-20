import React from "react";
import { FlatList, SafeAreaView, StyleSheet, Text, View } from "react-native";
import InfoCard from "../components/InfoCard";
import PrimaryButton from "../components/PrimaryButton";
import { buildClientEpisode } from "../components/episodeCatalog";
import { palette } from "../theme/palette";

export default function EpisodesScreen({ navigation, route }) {
  const connection = route.params?.connection;
  const library = route.params?.library;
  const season = route.params?.season;
  const episodes = season?.episodes || [];

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        contentContainerStyle={styles.content}
        data={episodes}
        keyExtractor={(item, index) => `${item.relativePath}-${index}`}
        ListHeaderComponent={
          <View style={styles.header}>
            <Text style={styles.helper}>
              Biblioteca: {library?.name} | Carpeta: {library?.relativePath}
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.row}>
            <InfoCard
              title={`E${String(item.episodeNumber || 0).padStart(2, "0")} · ${item.file}`}
              subtitle={item.relativePath}
              rightText={item.id}
            />
            <PrimaryButton
              label="Abrir ficha"
              onPress={() =>
                navigation.navigate("EpisodeDetail", {
                  connection,
                  library,
                  episode: buildClientEpisode(item, library?.name || "biblioteca"),
                })
              }
            />
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: palette.background,
  },
  content: {
    padding: 18,
  },
  header: {
    marginBottom: 12,
  },
  helper: {
    color: palette.muted,
  },
  row: {
    gap: 10,
    marginBottom: 14,
  },
});
