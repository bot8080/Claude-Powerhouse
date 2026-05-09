import { View, Text, StyleSheet, Pressable } from 'react-native';
import { colors } from '@constants/colors';

export default function PaymentScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Checkout</Text>
      <Text style={styles.subtitle}>Payment integration placeholder.</Text>
      <Pressable style={styles.button} accessibilityRole="button">
        <Text style={styles.buttonText}>Pay Now</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    paddingHorizontal: 24,
  },
  title: { fontSize: 24, fontWeight: '700', color: colors.text, marginBottom: 8 },
  subtitle: { fontSize: 16, color: colors.textSecondary, marginBottom: 24 },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingHorizontal: 32,
    paddingVertical: 12,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: { fontSize: 16, fontWeight: '600', color: colors.onBrand },
});
