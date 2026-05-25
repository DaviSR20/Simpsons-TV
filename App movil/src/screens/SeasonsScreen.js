import React, { useMemo } from "react";
import { FlatList, SafeAreaView, StyleSheet, Text, View } from "react-native";
import InfoCard from "../components/InfoCard";
import PrimaryButton from "../components/PrimaryButton";
import SectionTitle from "../components/SectionTitle";
import { palette } from "../theme/palette";
import images from "../../../episodes/images";

function groupBySeason(videos) {
  const map = new Map();

  for (const video of videos || []) {
    const seasonNumber = video.seasonNumber || 0;
    if (!map.has(seasonNumber)) {
      map.set(seasonNumber, []);
    }
    map.get(seasonNumber).push(video);
  }

  return Array.from(map.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([seasonNumber, seasonVideos]) => ({
      seasonNumber,
      title: `Temporada ${seasonNumber}`,
      episodes: seasonVideos.sort((a, b) => (a.episodeNumber || 0) - (b.episodeNumber || 0)),
    }));
}

export default function SeasonsScreen({ navigation, route }) {
  const connection = route.params?.connection;
  const library = route.params?.library;
  const seasons = useMemo(() => groupBySeason(library?.videos || []), [library]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        contentContainerStyle={styles.content}
        data={seasons}
        keyExtractor={(item) => String(item.seasonNumber)}
        ListHeaderComponent={
          <View style={styles.header}>
            <SectionTitle>{library?.name || "Temporadas"}</SectionTitle>
            <Text style={styles.helper}>
              El servidor del profesor está agrupando los vídeos desde la carpeta `{library?.relativePath}`.
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.row}>
            <InfoCard
              title={item.title}
              subtitle={`${item.episodes.length} episodios`}
              rightText={`S${String(item.seasonNumber).padStart(2, "0")}`}
              imageSource={images[`Season_${item.seasonNumber}_Icon.webp`]}
            />
            <PrimaryButton
              label="Ver episodios"
              onPress={() =>
                navigation.navigate("Episodes", {
                  connection,
                  library,
                  season: item,
                  seasonTitle: item.title,
                })
              }
            />
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No hay temporadas legibles en esta biblioteca.</Text>}
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
    gap: 10,
    marginBottom: 16,
  },
  helper: {
    color: palette.muted,
    lineHeight: 20,
  },
  row: {
    gap: 10,
    marginBottom: 14,
  },
  empty: {
    color: palette.muted,
    textAlign: "center",
    marginTop: 40,
  },
});
