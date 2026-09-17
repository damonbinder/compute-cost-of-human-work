export const PROGRAMS = [
  {
    id: 'us-snap',
    country: 'US',
    name: 'Supplemental Nutrition Assistance Program (SNAP)',
    description:
      'Provides monthly food benefits to low-income households so they can buy groceries and maintain nutritional health.',
    estimatedBenefit:
      'Average $150–$450 per month loaded onto an EBT card, depending on household size and income.',
    application:
      'Submit an application through your state Department of Social Services or the online SNAP portal. An eligibility interview is typically required.',
    website: 'https://www.fns.usda.gov/snap/state-directory',
    phone: '1-800-221-5689',
    nextSteps: [
      'Gather proof of identity, income, and household expenses.',
      'Complete your state SNAP application online or visit your local SNAP office.',
      'Attend the eligibility interview and respond quickly to any follow-up requests.'
    ],
    eligibility: ({ country, incomePerPerson }) =>
      country === 'US' && incomePerPerson <= 1500
  },
  {
    id: 'us-eitc',
    country: 'US',
    name: 'Earned Income Tax Credit (EITC)',
    description:
      'Refundable federal tax credit for low-to-moderate income workers and families, especially those with children.',
    estimatedBenefit:
      'Up to $7,430 annually at tax time, based on income, marital status, and number of qualifying children.',
    application:
      'Claim the credit when filing your annual federal tax return. Free preparation help is available through IRS VITA sites.',
    website: 'https://www.irs.gov/eitc',
    phone: '1-800-829-1040',
    nextSteps: [
      'Keep records of your earned income and number of qualifying dependents.',
      'File your federal tax return using IRS Free File or a VITA volunteer site.',
      'Check state EITC programs—many states offer additional credits.'
    ],
    eligibility: ({ country, employmentStatus, monthlyIncome, age, childrenUnder18 }) =>
      country === 'US' &&
      monthlyIncome <= 4500 &&
      (employmentStatus === 'Employed' || employmentStatus === 'Self-employed') &&
      age >= 25 &&
      age <= 64 &&
      (childrenUnder18 > 0 || monthlyIncome <= 3000)
  },
  {
    id: 'us-tanf',
    country: 'US',
    name: 'Temporary Assistance for Needy Families (TANF)',
    description:
      'Cash assistance and employment support for very low-income families with children.',
    estimatedBenefit:
      '$300–$800 per month in cash assistance plus access to job training and childcare support.',
    application:
      'Apply through your state TANF or Human Services office. Interviews and verification documents are required.',
    website: 'https://www.acf.hhs.gov/ofa/programs/tanf',
    phone: 'Call your local Human Services office (varies by state)',
    nextSteps: [
      'Contact your local TANF office to confirm documentation requirements.',
      'Submit proof of income, residency, and custody of children under 18.',
      'Enroll in required work activities or training programs to keep benefits.'
    ],
    eligibility: ({ country, monthlyIncome, householdSize, employmentStatus, childrenUnder18 }) =>
      country === 'US' &&
      childrenUnder18 > 0 &&
      monthlyIncome <= 1000 + householdSize * 250 &&
      (employmentStatus === 'Unemployed' || employmentStatus === 'Student' || monthlyIncome <= 1500)
  },
  {
    id: 'us-medicaid',
    country: 'US',
    name: 'Medicaid',
    description:
      'Free or low-cost health coverage for eligible low-income adults, children, pregnant people, older adults, and people with disabilities.',
    estimatedBenefit:
      'Comprehensive health coverage with little to no premiums or copayments.',
    application:
      'Apply via your state Medicaid agency or the Health Insurance Marketplace.',
    website: 'https://www.medicaid.gov/about-us/contact-us/index.html',
    phone: '1-877-267-2323',
    nextSteps: [
      'Submit proof of income, citizenship, and residency through your state portal.',
      'Report any special medical circumstances, disability status, or pregnancy.',
      'Complete annual recertification to maintain coverage.'
    ],
    eligibility: ({ country, monthlyIncome, householdSize, specialCircumstances }) => {
      if (country !== 'US') return false;
      const baseLimit = 1800 + (householdSize - 1) * 400;
      const qualifiesByIncome = monthlyIncome <= baseLimit;
      const qualifiesByCircumstance =
        specialCircumstances.disability ||
        specialCircumstances.pregnancy ||
        specialCircumstances.elderlyCare;
      return qualifiesByIncome || qualifiesByCircumstance;
    }
  },
  {
    id: 'us-wic',
    country: 'US',
    name: 'Special Supplemental Nutrition Program for Women, Infants, and Children (WIC)',
    description:
      'Nutrition support for pregnant and postpartum people and children under age 5.',
    estimatedBenefit:
      'Monthly food packages worth $50–$150, nutrition education, and breastfeeding support.',
    application:
      'Apply at your local WIC clinic. An in-person appointment with documentation is required.',
    website: 'https://www.fns.usda.gov/wic/wic-how-apply',
    phone: '1-800-942-3678',
    nextSteps: [
      'Call your local WIC office to schedule an intake appointment.',
      'Bring proof of identity, residency, income, and your child’s immunization record.',
      'Complete a brief nutrition assessment during the appointment.'
    ],
    eligibility: ({ country, childrenUnder18, specialCircumstances, age }) =>
      country === 'US' &&
      (specialCircumstances.pregnancy || childrenUnder18 > 0) &&
      age <= 55
  },
  {
    id: 'ng-nsip',
    country: 'Nigeria',
    name: 'National Social Investment Program (NSIP)',
    description:
      'Federal safety net that provides stipends and skills training for low-income households, including the N-Power and GEEP initiatives.',
    estimatedBenefit:
      '₦20,000–₦30,000 monthly stipends plus entrepreneurial loans or vocational training.',
    application:
      'Register through the NSIP portal or at local government offices during enrollment drives.',
    website: 'https://nsip.gov.ng',
    phone: '+234-803-123-4567',
    nextSteps: [
      'Create an account on the NSIP portal during an open registration window.',
      'Submit national ID, BVN, and current income information.',
      'Participate in onboarding sessions or skills assessments if selected.'
    ],
    eligibility: ({ country, incomePerPerson, employmentStatus, specialCircumstances }) =>
      country === 'Nigeria' &&
      incomePerPerson <= 35000 &&
      (employmentStatus === 'Unemployed' || specialCircumstances.disability)
  },
  {
    id: 'ng-ctovc',
    country: 'Nigeria',
    name: 'Conditional Cash Transfer for Orphans and Vulnerable Children (CT-OVC)',
    description:
      'Cash transfers to caregivers of orphans and vulnerable children to reduce poverty and improve education and health outcomes.',
    estimatedBenefit: '₦10,000–₦15,000 per month with additional education grants.',
    application:
      'Enroll through community-based targeting or local social welfare offices.',
    website: 'https://ncto.gov.ng',
    phone: '+234-700-2255-6826',
    nextSteps: [
      'Visit your local social welfare office to register vulnerable children in your care.',
      'Provide birth certificates, school enrollment records, and caregiver identification.',
      'Attend monthly community meetings to maintain enrollment.'
    ],
    eligibility: ({ country, childrenUnder18, specialCircumstances }) =>
      country === 'Nigeria' &&
      childrenUnder18 > 0 &&
      (specialCircumstances.elderlyCare || specialCircumstances.disability || childrenUnder18 >= 2)
  },
  {
    id: 'br-bolsa',
    country: 'Brazil',
    name: 'Bolsa Família (Auxílio Brasil)',
    description:
      'Conditional cash transfer program supporting low-income Brazilian families with children and pregnant people.',
    estimatedBenefit:
      'R$600 base payment per household with additional amounts for each child or pregnant dependent.',
    application:
      'Register with Cadastro Único at a local CRAS social assistance center.',
    website: 'https://www.gov.br/cidadania/pt-br/bolsa-familia',
    phone: '121 (Ministério da Cidadania hotline)',
    nextSteps: [
      'Visit a CRAS center with identification, proof of income, and residency documents.',
      'Complete Cadastro Único enrollment for your entire household.',
      'Ensure children attend school and follow health check-ups to keep benefits.'
    ],
    eligibility: ({ country, incomePerPerson, specialCircumstances, childrenUnder18 }) =>
      country === 'Brazil' &&
      incomePerPerson <= 1400 &&
      (childrenUnder18 > 0 || specialCircumstances.pregnancy)
  },
  {
    id: 'in-pmkisan',
    country: 'India',
    name: 'Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)',
    description:
      'Income support scheme providing ₹6,000 per year to eligible small and marginal farmers in three installments.',
    estimatedBenefit: '₹2,000 paid three times a year directly into beneficiaries’ bank accounts.',
    application:
      'Register through your state agriculture department or the PM-KISAN portal with land and Aadhaar details.',
    website: 'https://pmkisan.gov.in',
    phone: '155261 or 011-24300606',
    nextSteps: [
      'Gather Aadhaar, bank account information, and landholding records.',
      'Apply online via the PM-KISAN portal or visit your local CSC/gram panchayat.',
      'Track application status on the portal and update records if your details change.'
    ],
    eligibility: ({ country, monthlyIncome, employmentStatus }) =>
      country === 'India' &&
      monthlyIncome <= 20000 &&
      (employmentStatus === 'Self-employed' || employmentStatus === 'Employed')
  },
  {
    id: 'in-pmjay',
    country: 'India',
    name: 'Pradhan Mantri Jan Arogya Yojana (PM-JAY)',
    description:
      'Government health insurance scheme offering free hospitalization coverage for poor and vulnerable families.',
    estimatedBenefit: 'Up to ₹5 lakh per family per year for secondary and tertiary care hospitalization.',
    application:
      'Check eligibility on the PM-JAY portal and visit an empanelled hospital or CSC to enroll.',
    website: 'https://pmjay.gov.in',
    phone: '14555 or 1800-111-565',
    nextSteps: [
      'Search for your family on the PM-JAY eligibility list online.',
      'Visit the nearest empanelled hospital or CSC with ID proof to generate an e-card.',
      'Use the e-card at network hospitals for cashless treatment.'
    ],
    eligibility: ({ country, incomePerPerson, specialCircumstances }) =>
      country === 'India' &&
      (incomePerPerson <= 12000 || specialCircumstances.disability || specialCircumstances.elderlyCare)
  },
  {
    id: 'ke-ctovc',
    country: 'Kenya',
    name: 'Cash Transfer for Orphans and Vulnerable Children (CT-OVC)',
    description:
      'Bi-monthly cash transfers to poor households caring for orphans and vulnerable children.',
    estimatedBenefit: 'KSh 4,000 every two months deposited into a bank or mobile money account.',
    application:
      'Community committees identify eligible households; you can also register at the Department of Children Services.',
    website: 'https://socialprotection.go.ke',
    phone: '+254-0734-777-000',
    nextSteps: [
      'Report to your local Children’s Office with identification and details of children in your care.',
      'Open a bank or mobile money account to receive payments.',
      'Attend beneficiary meetings and comply with monitoring visits.'
    ],
    eligibility: ({ country, childrenUnder18, incomePerPerson }) =>
      country === 'Kenya' && childrenUnder18 > 0 && incomePerPerson <= 20000
  },
  {
    id: 'id-pkh',
    country: 'Indonesia',
    name: 'Program Keluarga Harapan (PKH)',
    description:
      'Conditional cash transfer program for very poor Indonesian households with pregnant women, young children, students, or older adults.',
    estimatedBenefit:
      'IDR 900,000–3,000,000 per year depending on family composition, paid quarterly.',
    application:
      'Register with the Integrated Social Welfare Data (DTKS) through your village office.',
    website: 'https://kemensos.go.id/program-keluarga-harapan',
    phone: '1500-771 (Ministry of Social Affairs hotline)',
    nextSteps: [
      'Report to your village or urban ward office to ensure your household is listed in DTKS.',
      'Provide family cards, IDs, and proof of school enrollment or prenatal checkups.',
      'Participate in Family Development Sessions to maintain eligibility.'
    ],
    eligibility: ({ country, incomePerPerson, specialCircumstances, childrenUnder18 }) =>
      country === 'Indonesia' &&
      incomePerPerson <= 2200000 &&
      (childrenUnder18 > 0 || specialCircumstances.pregnancy || specialCircumstances.elderlyCare)
  }
];

export const SUPPORTED_COUNTRIES = [
  { code: 'US', label: 'United States' },
  { code: 'Nigeria', label: 'Nigeria' },
  { code: 'Brazil', label: 'Brazil' },
  { code: 'India', label: 'India' },
  { code: 'Kenya', label: 'Kenya' },
  { code: 'Indonesia', label: 'Indonesia' }
];
