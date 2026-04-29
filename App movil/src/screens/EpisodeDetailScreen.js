import React, { useState } from "react";
import { Alert, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";
import PrimaryButton from "../components/PrimaryButton";
import InfoCard from "../components/InfoCard";
import { fetchNow, playEpisode, stopPlayback, volumeDown, volumeUp } from "../api/serverApi";
import { palette } from "../theme/palette";

export default function EpisodeDetailScreen({ route }) {
  const connection = route.params?.connection;
  const library = route.params?.library;
  const episode = route.params?.episode;
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  async function handlePlay() {
    setBusy(true);
    try {
      const result = await playEpisode(
        connection.baseUrl,
        connection.pin,
        episode.id,
        library.relativePath
      );
      setStatus(`Reproduciendo ${result.playing} en ${result.directory}`);
    } catch (error) {
      setStatus(error.message || "No se pudo lanzar la reproducción.");
    } finally {
      setBusy(false);
    }
  }

  async function handleStop() {
    setBusy(true);
    try {
      await stopPlayback(connection.baseUrl, connection.pin);
      setStatus("Reproducción detenida.");
    } catch (error) {
      setStatus(error.message || "No se pudo parar la reproducción.");
    } finally {
      setBusy(false);
    }
  }

  async function handleNow() {
    setBusy(true);
    try {
      const now = await fetchNow(connection.baseUrl, connection.pin);
      Alert.alert("Estado remoto", JSON.stringify(now, null, 2));
    } catch (error) {
      setStatus(error.message || "No se pudo consultar el estado.");
    } finally {
      setBusy(false);
    }
  }

  async function handleVolumeUp() {
    try {
      await volumeUp(connection.baseUrl, connection.pin);
      setStatus("Volumen subido.");
    } catch (error) {
      setStatus(error.message || "No se pudo subir el volumen.");
    }
  }

  async function handleVolumeDown() {
    try {
      await volumeDown(connection.baseUrl, connection.pin);
      setStatus("Volumen bajado.");
    } catch (error) {
      setStatus(error.message || "No se pudo bajar el volumen.");
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content}>
        <InfoCard
          title={episode.title}
          subtitle={`ID servidor: ${episode.id}`}
          rightText={`T${String(episode.seasonNumber).padStart(2, "0")}E${String(
            episode.episodeNumber
          ).padStart(2, "0")}`}
        />

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Ruta</Text>
          <Text style={styles.body}>{episode.directoryPath}</Text>
          <Text style={styles.sectionTitle}>Sinopsis</Text>
          <Text style={styles.body}>{episode.synopsis}</Text>
        </View>

        <View style={styles.actions}>
          <PrimaryButton label="Play en Raspberry" onPress={handlePlay} disabled={busy} />
          <PrimaryButton label="Stop" onPress={handleStop} tone="danger" disabled={busy} />
          <PrimaryButton label="Estado actual" onPress={handleNow} tone="secondary" disabled={busy} />
          <PrimaryButton label="Volumen +" onPress={handleVolumeUp} tone="secondary" />
          <PrimaryButton label="Volumen -" onPress={handleVolumeDown} tone="secondary" />
        </View>

        {status ? <Text style={styles.status}>{status}</Text> : null}
      </ScrollView>
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
    gap: 16,
  },
  card: {
    backgroundColor: palette.card,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: palette.border,
    padding: 16,
    gap: 8,
  },
  sectionTitle: {
    color: palette.text,
    fontSize: 15,
    fontWeight: "800",
  },
  body: {
    color: palette.muted,
    lineHeight: 21,
  },
  actions: {
    gap: 10,
  },
  status: {
    color: palette.accent,
    lineHeight: 20,
  },
});
