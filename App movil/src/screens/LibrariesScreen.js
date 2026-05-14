import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import InfoCard from "../components/InfoCard";
import PrimaryButton from "../components/PrimaryButton";
import SectionTitle from "../components/SectionTitle";
import { fetchHealth, fetchNow, fetchVideos, ledOff, ledOn } from "../api/serverApi";
import { palette } from "../theme/palette";

export default function LibrariesScreen({ navigation, route }) {
  const connection = route.params?.connection;
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [status, setStatus] = useState("");
  const [health, setHealth] = useState(route.params?.connection?.health || null);
  const [now, setNow] = useState(null);
  const [libraries, setLibraries] = useState([]);
  const [ledStateText, setLedStateText] = useState(route.params?.connection?.ledMessage || "");

  const loadData = useCallback(async () => {
    if (!connection?.baseUrl || !connection?.pin) {
      return;
    }

    const [healthPayload, videosPayload, nowPayload] = await Promise.all([
      fetchHealth(connection.baseUrl, connection.pin),
      fetchVideos(connection.baseUrl, connection.pin),
      fetchNow(connection.baseUrl, connection.pin),
    ]);

    setHealth(healthPayload);
    setNow(nowPayload);
    setLibraries(videosPayload.directories || []);
    setStatus(videosPayload.directories?.length ? "" : "El servidor no ha devuelto bibliotecas.");
  }, [connection]);

  useEffect(() => {
    let active = true;
    loadData()
      .catch((error) => {
        if (active) {
          setStatus(error.message || "No se pudo cargar el servidor.");
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [loadData]);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await loadData();
    } catch (error) {
      setStatus(error.message || "No se pudo refrescar.");
    } finally {
      setRefreshing(false);
    }
  }

  async function handleLedOn() {
    try {
      await ledOn(connection.baseUrl, connection.pin);
      setLedStateText("LED azul encendido.");
    } catch (error) {
      setLedStateText(error.message || "No se pudo encender el LED azul.");
    }
  }

  async function handleLedOff() {
    try {
      await ledOff(connection.baseUrl, connection.pin);
      setLedStateText("LED azul apagado.");
    } catch (error) {
      setLedStateText(error.message || "No se pudo apagar el LED azul.");
    }
  }

  if (loading) {
    return (
      <SafeAreaView style={styles.centered}>
        <ActivityIndicator color={palette.primary} size="large" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        contentContainerStyle={styles.content}
        data={libraries}
        keyExtractor={(item) => item.relativePath}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} tintColor={palette.primary} />}
        ListHeaderComponent={
          <View style={styles.header}>
            <SectionTitle>Contenido de la Raspberry</SectionTitle>
            <InfoCard
              title={connection.baseUrl}
              subtitle={`Reproduciendo: ${now?.playing || "nada ahora mismo"}`}
              rightText={health?.running ? "PLAY" : "IDLE"}
            />
            <View style={styles.ledActions}>
              <PrimaryButton label="LED ON" onPress={handleLedOn} />
              <PrimaryButton label="LED OFF" onPress={handleLedOff} tone="secondary" />
            </View>
            {ledStateText ? <Text style={styles.ledText}>{ledStateText}</Text> : null}
            <Text style={styles.helper}>
              Selecciona una biblioteca para ver temporadas y lanzar episodios.
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.libraryCard}>
            <InfoCard
              title={item.name}
              subtitle={`${item.videoCount} vídeos | ${item.episodeCount} episodios`}
              rightText={item.relativePath}
            />
            <View style={styles.cardActions}>
              <PrimaryButton
                label="Abrir"
                onPress={() =>
                  navigation.navigate("Seasons", {
                    connection,
                    library: item,
                    libraryName: item.name,
                  })
                }
              />
            </View>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>{status || "No hay bibliotecas visibles."}</Text>}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: palette.background,
  },
  centered: {
    flex: 1,
    backgroundColor: palette.background,
    alignItems: "center",
    justifyContent: "center",
  },
  content: {
    padding: 18,
    gap: 14,
  },
  header: {
    gap: 14,
    marginBottom: 6,
  },
  helper: {
    color: palette.muted,
    lineHeight: 20,
  },
  ledActions: {
    gap: 10,
  },
  ledText: {
    color: palette.primary,
    fontWeight: "700",
    lineHeight: 20,
  },
  libraryCard: {
    gap: 10,
    marginBottom: 14,
  },
  cardActions: {
    gap: 10,
  },
  empty: {
    color: palette.muted,
    textAlign: "center",
    marginTop: 32,
  },
});
