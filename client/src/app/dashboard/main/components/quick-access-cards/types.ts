export interface AccessCard {
  title: string;
  description: string;
  icon: string;
  link: string;
  linkText: string;
  gradientFrom: string;
  gradientTo: string;
  buttonColor: string;
}

export interface QuickAccessCardsProps {
  cards: AccessCard[];
}
