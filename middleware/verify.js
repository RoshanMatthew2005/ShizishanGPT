/**
 * Verification Script
 * Checks if all required files exist
 */

const fs = require('fs');
const path = require('path');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Required files and directories
const requiredFiles = [
  'server.js',
  'package.json',
  '.env.example',
  '.gitignore',
  'test.js',
  'config/env.js',
  'config/logger.js',
  'services/apiClient.js',
  'services/validator.js',
  'services/formatter.js',
  'middleware/requestLogger.js',
  'middleware/errorHandler.js',
  'middleware/validateInput.js',
  'controllers/llmController.js',
  'controllers/ragController.js',
  'controllers/yieldController.js',
  'controllers/weatherController.js',
  'controllers/pestController.js',
  'controllers/translateController.js',
  'routes/llmRouter.js',
  'routes/ragRouter.js',
  'routes/yieldRouter.js',
  'routes/weatherRouter.js',
  'routes/pestRouter.js',
  'routes/translateRouter.js',
  'README.md',
  'QUICKSTART.md',
  'INSTALL.md',
  'REACT_INTEGRATION.md',
  'BUILD_SUMMARY.md',
  'MILESTONE_5_COMPLETE.md',
  'FINAL_SUMMARY.md',
  'DIRECTORY_STRUCTURE.md'
];

function checkFile(filePath) {
  const fullPath = path.join(__dirname, filePath);
  const exists = fs.existsSync(fullPath);
  
  if (exists) {
    const stats = fs.statSync(fullPath);
    const size = stats.size;
    log(`✓ ${filePath} (${size} bytes)`, 'green');
    return true;
  } else {
    log(`✗ ${filePath} - MISSING`, 'red');
    return false;
  }
}

function checkPackageJson() {
  try {
    const packagePath = path.join(__dirname, 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    log('\n📦 Package.json Check:', 'blue');
    log(`   Name: ${packageJson.name}`, 'green');
    log(`   Version: ${packageJson.version}`, 'green');
    
    const requiredDeps = [
      'express', 'axios', 'dotenv', 'cors', 'joi', 
      'winston', 'helmet', 'compression', 'express-rate-limit'
    ];
    
    const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies[dep]);
    
    if (missingDeps.length > 0) {
      log(`   Missing dependencies: ${missingDeps.join(', ')}`, 'red');
      return false;
    } else {
      log(`   ✓ All required dependencies present`, 'green');
      return true;
    }
  } catch (error) {
    log(`   ✗ Error reading package.json: ${error.message}`, 'red');
    return false;
  }
}

function checkNodeModules() {
  const nodeModulesPath = path.join(__dirname, 'node_modules');
  const exists = fs.existsSync(nodeModulesPath);
  
  log('\n📚 Node Modules Check:', 'blue');
  if (exists) {
    log('   ✓ node_modules directory exists', 'green');
    log('   Run "npm install" if you see module errors', 'yellow');
    return true;
  } else {
    log('   ✗ node_modules NOT FOUND', 'red');
    log('   ⚠️  Run "npm install" to install dependencies', 'yellow');
    return false;
  }
}

function checkEnvFile() {
  const envPath = path.join(__dirname, '.env');
  const envExamplePath = path.join(__dirname, '.env.example');
  
  log('\n⚙️  Environment Check:', 'blue');
  
  if (!fs.existsSync(envExamplePath)) {
    log('   ✗ .env.example NOT FOUND', 'red');
    return false;
  } else {
    log('   ✓ .env.example exists', 'green');
  }
  
  if (!fs.existsSync(envPath)) {
    log('   ⚠️  .env NOT FOUND', 'yellow');
    log('   Copy .env.example to .env and configure it', 'yellow');
    return false;
  } else {
    log('   ✓ .env exists', 'green');
    return true;
  }
}

function main() {
  log('\n========================================', 'blue');
  log('Middleware Installation Verification', 'blue');
  log('========================================\n', 'blue');
  
  log('📁 Checking File Structure...\n', 'blue');
  
  let allFilesExist = true;
  const categories = {
    'Core': requiredFiles.slice(0, 5),
    'Config': requiredFiles.slice(5, 7),
    'Services': requiredFiles.slice(7, 10),
    'Middleware': requiredFiles.slice(10, 13),
    'Controllers': requiredFiles.slice(13, 19),
    'Routes': requiredFiles.slice(19, 25),
    'Documentation': requiredFiles.slice(25)
  };
  
  for (const [category, files] of Object.entries(categories)) {
    log(`\n${category}:`, 'blue');
    for (const file of files) {
      const exists = checkFile(file);
      if (!exists) allFilesExist = false;
    }
  }
  
  // Check package.json
  const packageOk = checkPackageJson();
  
  // Check node_modules
  const nodeModulesOk = checkNodeModules();
  
  // Check environment
  const envOk = checkEnvFile();
  
  // Summary
  log('\n========================================', 'blue');
  log('Verification Summary', 'blue');
  log('========================================\n', 'blue');
  
  const totalFiles = requiredFiles.length;
  const foundFiles = requiredFiles.filter(f => 
    fs.existsSync(path.join(__dirname, f))
  ).length;
  
  log(`Files: ${foundFiles}/${totalFiles}`, foundFiles === totalFiles ? 'green' : 'red');
  log(`Package.json: ${packageOk ? '✓' : '✗'}`, packageOk ? 'green' : 'red');
  log(`Node Modules: ${nodeModulesOk ? '✓' : '⚠️'}`, nodeModulesOk ? 'green' : 'yellow');
  log(`Environment: ${envOk ? '✓' : '⚠️'}`, envOk ? 'green' : 'yellow');
  
  log('\n========================================\n', 'blue');
  
  if (allFilesExist && packageOk) {
    log('✅ All core files present!', 'green');
    
    if (!nodeModulesOk) {
      log('\n⚠️  Next step: Run "npm install"', 'yellow');
    } else if (!envOk) {
      log('\n⚠️  Next step: Copy .env.example to .env and configure', 'yellow');
    } else {
      log('\n🚀 Ready to start! Run "npm start"', 'green');
    }
  } else {
    log('❌ Some files are missing. Please check the errors above.', 'red');
    process.exit(1);
  }
  
  log('');
}

main();
