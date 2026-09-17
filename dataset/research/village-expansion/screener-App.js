import React, { useState } from 'react';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import EligibilityWizard from './components/EligibilityWizard';
import ProgramRecommendations from './components/ProgramRecommendations';
import { PROGRAMS } from './data/programs';

const theme = {
  colors: {
    primary: '#1E88E5',
    secondary: '#2E7D32',
    background: '#F1F5F9',
    surface: '#FFFFFF',
    text: '#1F2933',
    muted: '#5F6C80'
  },
  fonts: {
    heading: "'Poppins', 'Segoe UI', sans-serif",
    body: "'Inter', 'Segoe UI', sans-serif"
  }
};

const GlobalStyle = createGlobalStyle`
  *, *::before, *::after {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    font-family: ${theme.fonts.body};
    background: radial-gradient(circle at top left, rgba(30, 136, 229, 0.18), transparent 55%),
      radial-gradient(circle at bottom right, rgba(46, 125, 50, 0.18), transparent 50%),
      ${theme.colors.background};
    color: ${theme.colors.text};
    min-height: 100vh;
  }

  #root {
    min-height: 100vh;
  }
`;

function App() {
  const [formResult, setFormResult] = useState(null);
  const [eligiblePrograms, setEligiblePrograms] = useState([]);

  const handleEligibilityComplete = answers => {
    const matchedPrograms = PROGRAMS.filter(program => {
      try {
        return program.eligibility(answers);
      } catch (error) {
        console.error(`Eligibility check failed for ${program.name}`, error);
        return false;
      }
    });

    setFormResult(answers);
    setEligiblePrograms(matchedPrograms);
  };

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <AppShell>
        <HeroSection>
          <HeroBadge>Poverty Action Hub</HeroBadge>
          <HeroTitle>Poverty Action Hub Eligibility Screener</HeroTitle>
          <HeroSubtitle>Check Your Eligibility for Financial Assistance Programs</HeroSubtitle>
          <HeroDetails>
            <li>Compare federal and national benefits in minutes.</li>
            <li>See estimated support amounts and next steps to apply.</li>
            <li>Created with accessibility and privacy best practices in mind.</li>
          </HeroDetails>
        </HeroSection>

        <ContentGrid>
          <EligibilityWizard onComplete={handleEligibilityComplete} />
          <ProgramRecommendations programs={eligiblePrograms} formData={formResult} />
        </ContentGrid>
      </AppShell>
    </ThemeProvider>
  );
}

export default App;

const AppShell = styled.main`
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1.5rem 4rem;
  display: grid;
  gap: 2.5rem;

  @media (max-width: 768px) {
    padding: 2.5rem 1.25rem 3rem;
  }
`;

const HeroSection = styled.section`
  display: grid;
  gap: 1rem;
  text-align: left;
`;

const HeroBadge = styled.span`
  align-self: flex-start;
  background: rgba(46, 125, 50, 0.2);
  color: ${({ theme }) => theme.colors.secondary};
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-weight: 600;
  letter-spacing: 0.02em;
`;

const HeroTitle = styled.h1`
  margin: 0;
  font-family: ${({ theme }) => theme.fonts.heading};
  font-size: clamp(2rem, 5vw, 3rem);
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.1;
`;

const HeroSubtitle = styled.h2`
  margin: 0;
  font-size: clamp(1.1rem, 3vw, 1.5rem);
  color: ${({ theme }) => theme.colors.primary};
  font-weight: 600;
`;

const HeroDetails = styled.ul`
  margin: 0;
  padding-left: 1.25rem;
  display: grid;
  gap: 0.5rem;
  color: ${({ theme }) => theme.colors.muted};
  line-height: 1.6;
`;

const ContentGrid = styled.section`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  align-items: start;
`;
