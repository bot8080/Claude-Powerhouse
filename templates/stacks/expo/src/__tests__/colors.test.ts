import { colors } from '@constants/colors';

describe('colors', () => {
  it('exports the colors object', () => {
    expect(colors).toBeDefined();
  });

  it('has brand colors', () => {
    expect(colors.primary).toBe('#4A90D9');
    expect(colors.primaryLight).toBe('#7AB3F0');
  });

  it('has surface colors', () => {
    expect(colors.background).toBe('#F8F9FA');
    expect(colors.card).toBe('#FFFFFF');
  });

  it('has text colors', () => {
    expect(colors.text).toBe('#1A1A2E');
    expect(colors.textSecondary).toBe('#6B7280');
  });

  it('has semantic state colors', () => {
    expect(colors.success).toBe('#22C55E');
    expect(colors.warning).toBe('#F59E0B');
    expect(colors.error).toBe('#EF4444');
  });
});
