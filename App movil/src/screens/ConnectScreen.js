import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Modal,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import PrimaryButton from "../components/PrimaryButton";
import InfoCard from "../components/InfoCard";
import SectionTitle from "../components/SectionTitle";
import {
  authenticate,
  fetchHealth,
  ledOn,
  normalizeBaseUrl,
  parseQrPayload,
} from "../api/serverApi";
import { clearConnection, loadConnection, saveConnection } from "../storage/connectionStorage";
import { palette } from "../theme/palette";

export default function ConnectScreen({ navigation }) {
  const [permissions, requestPermission] = useCameraPermissions();
  const [baseUrl, setBaseUrl] = useState("");
  const [pin, setPin] = useState("1234");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [scannerOpen, setScannerOpen] = useState(false);
  const [scanLocked, setScanLocked] = useState(false);

  useEffect(() => {
    let active = true;
    loadConnection()
      .then((stored) => {
        if (!active || !stored) {
          return;
        }
        setBaseUrl(stored.baseUrl || "");
        setPin(stored.pin || "1234");
        setStatus(`Conexión guardada: ${stored.baseUrl}`);
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const canConnect = useMemo(() => Boolean(baseUrl.trim()) && Boolean(pin.trim()), [baseUrl, pin]);

  async function handleConnect() {
    const normalizedBaseUrl = normalizeBaseUrl(baseUrl);
    if (!normalizedBaseUrl || !pin.trim()) {
      setStatus("Introduce una URL válida y el PIN.");
      return;
    }

    setConnecting(true);
    try {
      await authenticate(normalizedBaseUrl, pin.trim());
      const health = await fetchHealth(normalizedBaseUrl, pin.trim());
      try {
        await ledOn(normalizedBaseUrl, pin.trim());
      } catch (ledError) {
        console.warn("No se pudo encender el LED azul:", ledError);
      }
      await saveConnection({
        baseUrl: normalizedBaseUrl,
        pin: pin.trim(),
      });
      setStatus(`Conectado a ${normalizedBaseUrl}`);
      navigation.replace("Libraries", {
        connection: {
          baseUrl: normalizedBaseUrl,
          pin: pin.trim(),
          health,
        },
      });
    } catch (error) {
      setStatus(error.message || "No se pudo conectar con la Raspberry.");
    } finally {
      setConnecting(false);
    }
  }

  async function handleScanQr({ data }) {
    if (scanLocked) {
      return;
    }

    setScanLocked(true);
    try {
      const parsed = parseQrPayload(data);
      setBaseUrl(parsed.baseUrl);
      setStatus(`QR leído: ${parsed.baseUrl}`);
      setScannerOpen(false);
    } catch {
      setStatus("El QR no contiene una URL válida del servidor.");
    } finally {
      setTimeout(() => setScanLocked(false), 800);
    }
  }

  async function handleClearSavedConnection() {
    await clearConnection();
    setBaseUrl("");
    setPin("1234");
    setStatus("Conexión guardada eliminada.");
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
      <ScrollView contentContainerStyle={styles.content}>
        <SectionTitle>Conectar con la tele</SectionTitle>
        <Text style={styles.lead}>
          Escanea el QR que muestra la Raspberry o escribe manualmente la URL del servidor.
        </Text>

        <InfoCard
          title="Servidor esperado"
          subtitle="Ejemplo: http://10.1.32.143:5050"
          rightText="Flask"
        />

        <View style={styles.formGroup}>
          <Text style={styles.label}>URL del servidor</Text>
          <TextInput
            value={baseUrl}
            onChangeText={setBaseUrl}
            placeholder="http://10.1.32.143:5050"
            placeholderTextColor={palette.muted}
            autoCapitalize="none"
            autoCorrect={false}
            style={styles.input}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>PIN web</Text>
          <TextInput
            value={pin}
            onChangeText={setPin}
            placeholder="1234"
            placeholderTextColor={palette.muted}
            keyboardType="number-pad"
            secureTextEntry={false}
            style={styles.input}
          />
        </View>

        <View style={styles.actions}>
          <PrimaryButton label="Escanear QR" onPress={() => setScannerOpen(true)} tone="secondary" />
          <PrimaryButton label="Conectar" onPress={handleConnect} disabled={!canConnect || connecting} />
        </View>

        <View style={styles.actions}>
          <PrimaryButton
            label="Borrar conexión guardada"
            onPress={handleClearSavedConnection}
            tone="danger"
          />
        </View>

        {connecting ? <ActivityIndicator color={palette.primary} size="small" /> : null}
        {status ? <Text style={styles.status}>{status}</Text> : null}
      </ScrollView>

      <Modal visible={scannerOpen} animationType="slide">
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Escanear QR de la Raspberry</Text>
            <PrimaryButton label="Cerrar" onPress={() => setScannerOpen(false)} tone="secondary" />
          </View>

          {!permissions?.granted ? (
            <View style={styles.permissionCard}>
              <Text style={styles.permissionText}>
                La app necesita permiso de cámara para leer el QR.
              </Text>
              <PrimaryButton
                label="Dar permiso"
                onPress={requestPermission}
                tone="primary"
              />
            </View>
          ) : (
            <CameraView
              style={styles.camera}
              facing="back"
              barcodeScannerSettings={{ barcodeTypes: ["qr"] }}
              onBarcodeScanned={handleScanQr}
            />
          )}
        </SafeAreaView>
      </Modal>
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
    gap: 16,
  },
  lead: {
    color: palette.muted,
    fontSize: 14,
    lineHeight: 21,
    marginBottom: 4,
  },
  formGroup: {
    gap: 8,
  },
  label: {
    color: palette.text,
    fontWeight: "800",
  },
  input: {
    backgroundColor: palette.card,
    color: palette.text,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: palette.border,
    paddingHorizontal: 14,
    paddingVertical: 14,
  },
  actions: {
    gap: 10,
  },
  status: {
    color: palette.accent,
    lineHeight: 20,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: "#000",
  },
  modalHeader: {
    padding: 16,
    gap: 12,
    backgroundColor: palette.background,
  },
  modalTitle: {
    color: palette.text,
    fontSize: 18,
    fontWeight: "800",
  },
  camera: {
    flex: 1,
  },
  permissionCard: {
    margin: 18,
    gap: 12,
    backgroundColor: palette.card,
    borderRadius: 16,
    padding: 18,
  },
  permissionText: {
    color: palette.text,
    lineHeight: 20,
  },
});
