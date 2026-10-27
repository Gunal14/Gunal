# 🧪 Professional Authentication - Testing Guide (Updated 2026)

## ⚡ Quick Start Testing

### 1. Start the Application
```bash
# Terminal - Navigate to project directory
cd "d:\major project"

# Start Flask server
python backend/main.py
# or
python -m flask --app backend.main run

# Server should start at http://localhost:5000
```

### 2. Visit Pages in Browser
```
Home Page:       http://localhost:5000/
Login Page:      http://localhost:5000/login
Register Page:   http://localhost:5000/register
Dashboard:       http://localhost:5000/dashboard
```

---

## 🏠 Home Page Testing

### Visual Elements
- [ ] Title displays: "AI SAFETY MONITORING"
- [ ] Subtitle: "Professional CCTV Security System"
- [ ] Logo with shield icon visible
- [ ] Navigation bar with "Login" and "Register" buttons
- [ ] 6 feature cards displayed
- [ ] Footer with copyright text

### Functionality
- [ ] "Sign In" button navigates to `/login`
- [ ] "Create Account" button navigates to `/register`
- [ ] All links in header work
- [ ] Page responsive on mobile


### Form Validation (Client-Side)

**Test: Empty Username**
```
1. Go to /login
2. Leave username empty
3. Click "Sign In"
Expected: 
  ✓ Error message appears: "Username required"
  ✓ Red border on username field
  ✓ No API call made
```

**Test: Invalid Credentials**
```
1. Enter username: "invaliduser123"
2. Enter password: "wrongpass"
3. Click "Sign In"
Expected:
  ✓ Loading spinner appears (1-2 seconds)
  ✓ API call made to /api/auth/login
  ✓ Error message: "Invalid username or password"
  ✓ Error dismisses automatically after 5 seconds
```

**Test: Valid Credentials**
```
1. Enter username: "demo_user"
2. Enter password: "demo_password"
3. Click "Sign In"
Expected:
  ✓ Loading spinner appears
  ✓ Token saved to localStorage
  ✓ Page redirects to /dashboard
```

---

## 📝 Registration Page Testing

### Step 1: Visual Elements
- [ ] "Create Account" heading visible
- [ ] All 7 form fields render:
  - [ ] First Name
  - [ ] Last Name
  - [ ] Email
  - [ ] Username
  - [ ] Password
  - [ ] Confirm Password
  - [ ] Role dropdown
- [ ] Password strength meter visible
- [ ] Terms checkbox present
- [ ] "Register" button functional

### Step 2: Password Strength Indicator

**Test: Empty Password**
```
Expected:
  ✓ Password strength bar empty
  ✓ No criteria checked
  ✓ Meter shows "Weak"
```

**Test: Add Special Character**
```
Type: "Passw0rd!"
Expected:
  ✓ Bar GREEN (5/5 criteria met)
  ✓ All 5 checks ✓
  ✓ Text: "Strong"
```

### Step 3: Form Validation

**Test: Required Fields**
```
Click "Register" with empty form
Expected:
  ✓ Error messages for all required fields
  ✓ No API call made
  ✓ User can correct and resubmit
```

**Test: Passwords Don't Match**
```
1. Password: "ValidPass123!"
2. Confirm: "DifferentPass456!"
3. Submit
Expected:
  ✓ Error: "Passwords do not match"
```

**Test: Valid Registration**
```
Fill all fields correctly + agree to terms
Expected:
  ✓ Loading spinner
  ✓ API call to /api/auth/register
  ✓ Success message
  ✓ Redirected to /login after 3s
```

---

## 🎛️ Dashboard Testing

### Authorization Tests

**Test: Unauthenticated Access**
```
1. Go to /dashboard (no login)
2. Browser dev tools → Application → Storage → Local Storage
Expected:
  ✓ localStorage is empty
  ✓ Redirect to home page (/)
```

**Test: Authenticated Access**
```
1. Complete login successfully
2. Go to /dashboard
Expected:
  ✓ Dashboard content visible
  ✓ Username in header
  ✓ System status indicator
```

**Test: Token Persistence**
```
1. Load dashboard (logged in)
2. Press F5 to refresh
Expected:
  ✓ Dashboard reloads without login
  ✓ Token retrieved from localStorage
```

**Test: Logout Functionality**
```
1. Load dashboard
2. Click "Logout" button
Expected:
  ✓ Token cleared from localStorage
  ✓ Redirect to home page
  ✓ Cannot access /dashboard anymore
```

---

## 🏃 Complete User Flow Test

### Workflow: New User Registration → Login → Dashboard → Logout

```
STEP 1: Visit Home Page
  URL: http://localhost:5000/
  Verify: Page loads, all elements visible

STEP 2: Click "Create Account"
  Verify: Navigates to /register

STEP 3: Fill Registration Form
  Fields:
    First Name: John
    Last Name: Doe
    email: john.doe.2026@example.com
    Username: john_doe_2026
    Password: SecurePass123!
    Confirm: SecurePass123!
    Role: operator
  Verify: Password strength shows GREEN (strong)
  Verify: Terms checkbox can be checked

STEP 4: Submit Registration
  Verify: Loading spinner appears
  Verify: Success message appears
  Verify: Redirected to /login after 3 seconds

STEP 5: Login with New Credentials
  URL: http://localhost:5000/login
  Enter:
    Username: john_doe_2026
    Password: SecurePass123!
  Verify: Loading spinner appears
  Verify: Redirected to /dashboard

STEP 6: Verify Dashboard Loaded
  Verify: Header shows username
  Verify: System status indicator active
  Verify: Safety cards visible
  Verify: Statistics displayed

STEP 7: Check Token Storage
  DevTools: F12 → Application → Storage → Local Storage
  Verify: access_token present
  Verify: user object present

STEP 8: Refresh Dashboard
  Key: F5 (refresh)
  Verify: Dashboard still loaded (token persisted)
  Verify: No re-login required

STEP 9: Logout
  Click: Logout button (bottom of sidebar)
  Verify: localStorage cleared
  Verify: Redirect to home page (/)

STEP 10: Verify Logout Complete
  Try: Access /dashboard directly
  Verify: Redirect to home page (/)
```

---

## 🔍 Browser DevTools Testing

### Console Tests (F12 → Console)
```javascript
// Check if already logged in
localStorage.getItem('access_token')
// Should return: null (if logged out) or "eyJ..." (if logged in)

// Check user info
JSON.parse(localStorage.getItem('user'))
// Should return: null or {user_id, username, email, role}

// Check for errors
// Should see NO red error messages
// May see yellow warnings (normal)
```

### Network Tab Tests (F12 → Network)
```
Perform Login:
  Watch Network requests
  Look for: POST /api/auth/login
  Status: 200 (success) or 401 (failure)
  Response: Should contain access_token

Perform Logout:
  Look for: POST /api/auth/logout
  Or check localStorage removal
```

### Storage Tab Tests (F12 → Application → Storage)
```
Before Login:
  localStorage should be EMPTY

After Login:
  access_token: "eyJhbGc..."
  user: "{"username":"test..."}"

After Logout:
  localStorage should be EMPTY again
```

---

## 📱 Mobile Responsiveness Testing

Using DevTools Device Toggle (F12 → Responsive Design Mode)

**iPhone 12 (390x844)**
- [ ] Text readable without zooming
- [ ] Buttons have 44px minimum tap target
- [ ] Feature cards single column
- [ ] No horizontal scroll
- [ ] Forms easy to fill

**iPad (810x1080)**
- [ ] Content properly centered
- [ ] Forms not too wide
- [ ] Touch targets adequate
- [ ] No weird layout shifts

---

## 🐛 Troubleshooting

### Problem: Pages show 404
```
Solution:
1. Check Flask is running (http://localhost:5000/health)
2. Verify template files exist in frontend/templates/
3. Check browser console for errors (F12)
```

### Problem: Styles not loading
```
Solution:
1. Check CSS file exists at frontend/static/css/style.css
2. DevTools → Elements → Styles (see if CSS linked)
3. Check Network tab for CSS request status
```

### Problem: Form validation not working
```
Solution:
1. Check browser console (F12 → Console) for JavaScript errors
2. Verify Orbitron font loads (check Network tab)
3. Try clearing browser cache (Ctrl+Shift+Delete)
```

### Problem: Login button not working
```
Solution:
1. Check Network tab (F12 → Network)
2. Look for failed API requests
3. Verify CORS is enabled
4. Check Firefox/Chrome console for CORS errors
```

### Problem: Token not saving in localStorage
```
Solution:
1. DevTools → Storage → Local Storage
2. Check if localStorage enabled in browser
3. Verify API returns valid token format
4. Check browser console for errors
```

---

## ✅ Final Checklist

Before declaring testing complete:

```
PAGES LOAD:
  ☐ / (home) loads without 404
  ☐ /login loads without 404
  ☐ /register loads without 404
  ☐ /dashboard loads without 404

STYLING:
  ☐ Orbitron font displays on all pages
  ☐ Colors match cybersecurity theme
  ☐ Animations are smooth
  ☐ No layout shifts on page load

USER FLOWS:
  ☐ Can register with valid data
  ☐ Can login after registration
  ☐ Can access dashboard when logged in
  ☐ Auto-redirects when not logged in
  ☐ Can logout and return to home

FORMS:
  ☐ Login form validates empty fields
  ☐ Registration validates all fields
  ☐ Password strength meter works
  ☐ Error messages display and auto-dismiss

MOBILE:
  ☐ All pages responsive
  ☐ Touch targets adequate
  ☐ No horizontal scroll
```

### 🚀 All Tests Pass?
⭐ **Ready for Production Deployment!**
