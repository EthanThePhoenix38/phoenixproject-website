// Import API catalog from external sources
// Run: node scripts/import-catalog.js

import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Sample catalog data structure
const catalogData = [
  {
    name: 'Web Scraper',
    category: 'Automation',
    description: 'Extract data from websites',
    url: 'https://api.example.com/scraper'
  },
  {
    name: 'Email Validator',
    category: 'Developer Tools',
    description: 'Validate email addresses',
    url: 'https://api.example.com/email-validator'
  },
  {
    name: 'Image Optimizer',
    category: 'Media',
    description: 'Compress and optimize images',
    url: 'https://api.example.com/image-optimizer'
  },
  {
    name: 'Sentiment Analysis',
    category: 'AI',
    description: 'Analyze text sentiment',
    url: 'https://api.example.com/sentiment'
  },
  {
    name: 'Currency Converter',
    category: 'Business',
    description: 'Convert between currencies',
    url: 'https://api.example.com/currency'
  }
];

async function importCatalog() {
  console.log('Importing catalog data...');

  const { data, error } = await supabase
    .from('api_catalog')
    .upsert(catalogData, { onConflict: 'url' });

  if (error) {
    console.error('Import failed:', error);
    process.exit(1);
  }

  console.log(`Imported ${catalogData.length} items`);
  console.log('Import complete');
}

importCatalog();
