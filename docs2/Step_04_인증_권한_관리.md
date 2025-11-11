# Step 4: 인증 및 권한 관리

> **목표**: Spring Security와 JWT를 활용한 사용자 인증 및 권한 관리를 구현한다.

---

## 🎯 이 단계를 배우는 이유

### 인증이 없으면?

지금까지 만든 API는 누구나 접근 가능합니다:
- ❌ 다른 사람 글도 마음대로 수정/삭제 가능
- ❌ 누가 작성했는지 알 수 없음
- ❌ 관리자 기능 구분 불가

### 프론트엔드에서 경험한 인증

```javascript
// 로그인
const login = async (email, password) => {
    const { token } = await fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
    
    localStorage.setItem('token', token);  // 토큰 저장
};

// 인증이 필요한 API 호출
const fetchPosts = async () => {
    const token = localStorage.getItem('token');
    return fetch('/api/posts', {
        headers: {
            'Authorization': `Bearer ${token}`  // 토큰 전송
        }
    });
};
```

이제 **백엔드에서 토큰을 발급하고 검증하는** 부분을 구현합니다.

---

## 💡 핵심 개념

### 1. 인증(Authentication) vs 인가(Authorization)

| 개념 | 의미 | 예시 |
|------|------|------|
| **인증** | "너 누구야?" | 로그인 (ID/PW 확인) |
| **인가** | "뭘 할 수 있어?" | 관리자만 삭제 가능 |

```
인증: 주민등록증 확인 (신원 확인)
인가: 나이 19세 이상만 출입 가능 (권한 확인)
```

### 2. 세션 vs 토큰 인증

#### 세션 방식 (전통적)
```
1. 로그인 성공
2. 서버가 세션 생성, 세션 ID를 쿠키로 전송
3. 클라이언트는 매 요청마다 쿠키 전송
4. 서버는 세션 ID로 사용자 확인

문제점:
- 서버에 세션 저장 (메모리 사용)
- 여러 서버 사용 시 세션 공유 어려움 (마이크로서비스 부적합)
```

#### 토큰 방식 (JWT)
```
1. 로그인 성공
2. 서버가 JWT 토큰 발급
3. 클라이언트는 토큰을 localStorage에 저장
4. 매 요청마다 헤더에 토큰 포함
5. 서버는 토큰만 검증 (세션 불필요)

장점:
- 서버 무상태 (Stateless)
- 확장 용이 (마이크로서비스 적합)
```

#### 프론트엔드 비유

```javascript
// 세션 = 쿠키 (자동 전송)
document.cookie = "sessionId=abc123";

// JWT = localStorage (수동 전송)
localStorage.setItem('token', 'eyJhbGciOiJIUzI1...');
fetch('/api/posts', {
    headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
});
```

---

### 3. JWT (JSON Web Token) 구조

```
JWT = Header.Payload.Signature

eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIn0.X4nKiHqJ...
└─────── Header ────────┘└──────── Payload ───────┘└─── Signature ──┘
```

#### Header (알고리즘 정보)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### Payload (사용자 정보)
```json
{
  "sub": "user@example.com",  // 사용자 식별자
  "role": "ROLE_USER",         // 권한
  "iat": 1234567890,           // 발급 시간
  "exp": 1234567890            // 만료 시간
}
```

#### Signature (서명)
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret-key
)
```

**중요**: Signature 때문에 토큰 위변조 불가능!

---

### 4. Spring Security란?

스프링의 **보안 프레임워크**로, 인증과 인가를 간단하게 구현할 수 있습니다.

#### Spring Security의 동작 과정

```
요청
 ↓
[Security Filter Chain]  ← 여러 개의 필터가 순차적으로 실행
 ↓ JWT Filter (우리가 만듦)
 ↓ 토큰 검증
 ↓ 사용자 정보 추출
 ↓
[Controller]
```

#### 프론트엔드 비유: Middleware

```javascript
// Express.js Middleware
app.use((req, res, next) => {
    const token = req.headers.authorization;
    if (!token) return res.status(401).send('Unauthorized');
    
    // 토큰 검증
    const user = verifyToken(token);
    req.user = user;  // 사용자 정보 추가
    next();
});

// Spring Security도 비슷 (Filter Chain)
```

---

## 🛠️ 최소 구현 코드

### 1. 의존성 추가

```gradle
// build.gradle

dependencies {
    // 기존 의존성들...
    
    // Spring Security
    implementation 'org.springframework.boot:spring-boot-starter-security'
    
    // JWT
    implementation 'io.jsonwebtoken:jjwt-api:0.12.3'
    runtimeOnly 'io.jsonwebtoken:jjwt-impl:0.12.3'
    runtimeOnly 'io.jsonwebtoken:jjwt-jackson:0.12.3'
}
```

---

### 2. User Entity 생성

```java
// src/main/java/com/project/board/model/User.java

package com.project.board.model;

import jakarta.persistence.*;
import lombok.Data;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "users")  // "user"는 예약어라서 "users" 사용
@Data
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, nullable = false)
    private String email;
    
    @Column(nullable = false)
    private String password;  // 암호화된 비밀번호 저장
    
    private String name;
    
    @Enumerated(EnumType.STRING)
    private Role role;  // ROLE_USER, ROLE_ADMIN
    
    @OneToMany(mappedBy = "author")
    private List<Post> posts = new ArrayList<>();
}
```

```java
// src/main/java/com/project/board/model/Role.java

package com.project.board.model;

public enum Role {
    ROLE_USER,   // 일반 사용자
    ROLE_ADMIN   // 관리자
}
```

```java
// Post Entity에 작성자 추가

@Entity
@Data
public class Post {
    // 기존 필드들...
    
    @ManyToOne
    @JoinColumn(name = "author_id")
    private User author;  // 작성자
}
```

---

### 3. JWT 유틸리티 클래스

```java
// src/main/java/com/project/board/security/JwtTokenProvider.java

package com.project.board.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.security.Key;
import java.util.Date;

@Component
public class JwtTokenProvider {
    
    private final Key key;
    private final long validityInMilliseconds;
    
    public JwtTokenProvider(
            @Value("${jwt.secret}") String secret,
            @Value("${jwt.expiration}") long validityInMilliseconds) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes());
        this.validityInMilliseconds = validityInMilliseconds;
    }
    
    // 토큰 생성
    public String createToken(String email, String role) {
        Date now = new Date();
        Date validity = new Date(now.getTime() + validityInMilliseconds);
        
        return Jwts.builder()
                .setSubject(email)
                .claim("role", role)
                .setIssuedAt(now)
                .setExpiration(validity)
                .signWith(key)
                .compact();
    }
    
    // 토큰에서 이메일 추출
    public String getEmail(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }
    
    // 토큰 검증
    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }
}
```

---

### 4. JWT 필터 생성

```java
// src/main/java/com/project/board/security/JwtAuthenticationFilter.java

package com.project.board.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    private final JwtTokenProvider jwtTokenProvider;
    private final UserDetailsService userDetailsService;
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        // 1. 헤더에서 토큰 추출
        String token = resolveToken(request);
        
        // 2. 토큰 검증
        if (token != null && jwtTokenProvider.validateToken(token)) {
            // 3. 토큰에서 이메일 추출
            String email = jwtTokenProvider.getEmail(token);
            
            // 4. 사용자 정보 로드
            UserDetails userDetails = userDetailsService.loadUserByUsername(email);
            
            // 5. 인증 객체 생성
            UsernamePasswordAuthenticationToken authentication =
                new UsernamePasswordAuthenticationToken(
                    userDetails, null, userDetails.getAuthorities()
                );
            
            // 6. SecurityContext에 저장
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }
        
        filterChain.doFilter(request, response);
    }
    
    // Authorization 헤더에서 토큰 추출
    private String resolveToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

---

### 5. Security 설정

```java
// src/main/java/com/project/board/config/SecurityConfig.java

package com.project.board.config;

import com.project.board.security.JwtAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {
    
    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())  // JWT 사용 시 CSRF 불필요
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)  // 세션 사용 안 함
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/h2-console/**").permitAll()  // 인증 불필요
                .requestMatchers("/api/admin/**").hasRole("ADMIN")  // 관리자만
                .anyRequest().authenticated()  // 나머지는 인증 필요
            )
            .addFilterBefore(jwtAuthenticationFilter, 
                            UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();  // 비밀번호 암호화
    }
}
```

---

### 6. 인증 Controller

```java
// src/main/java/com/project/board/controller/AuthController.java

package com.project.board.controller;

import com.project.board.dto.LoginRequest;
import com.project.board.dto.LoginResponse;
import com.project.board.dto.RegisterRequest;
import com.project.board.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
    
    private final AuthService authService;
    
    // POST /api/auth/register - 회원가입
    @PostMapping("/register")
    public ResponseEntity<String> register(@RequestBody RegisterRequest request) {
        authService.register(request);
        return ResponseEntity.ok("회원가입 성공");
    }
    
    // POST /api/auth/login - 로그인
    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest request) {
        String token = authService.login(request);
        return ResponseEntity.ok(new LoginResponse(token));
    }
}
```

```java
// DTO 클래스들

@Data
public class RegisterRequest {
    private String email;
    private String password;
    private String name;
}

@Data
public class LoginRequest {
    private String email;
    private String password;
}

@Data
@AllArgsConstructor
public class LoginResponse {
    private String token;
}
```

---

### 7. Auth Service

```java
// src/main/java/com/project/board/service/AuthService.java

package com.project.board.service;

import com.project.board.dto.LoginRequest;
import com.project.board.dto.RegisterRequest;
import com.project.board.model.Role;
import com.project.board.model.User;
import com.project.board.repository.UserRepository;
import com.project.board.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    
    public void register(RegisterRequest request) {
        // 이메일 중복 체크
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("이미 존재하는 이메일입니다.");
        }
        
        // 사용자 생성
        User user = new User();
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));  // 암호화
        user.setName(request.getName());
        user.setRole(Role.ROLE_USER);
        
        userRepository.save(user);
    }
    
    public String login(LoginRequest request) {
        // 사용자 조회
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new RuntimeException("사용자를 찾을 수 없습니다."));
        
        // 비밀번호 검증
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("비밀번호가 일치하지 않습니다.");
        }
        
        // JWT 토큰 생성
        return jwtTokenProvider.createToken(user.getEmail(), user.getRole().name());
    }
}
```

---

### 8. application.properties 추가

```properties
# JWT 설정
jwt.secret=your-secret-key-must-be-at-least-256-bits-long-for-HS256
jwt.expiration=86400000
# 86400000ms = 24시간
```

---

## 📝 실습 가이드

### Step 1: 회원가입 테스트
```
POST http://localhost:8080/api/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123",
    "name": "홍길동"
}
```

### Step 2: 로그인 테스트
```
POST http://localhost:8080/api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}

응답:
{
    "token": "eyJhbGciOiJIUzI1NiJ9..."
}
```

### Step 3: 인증이 필요한 API 호출
```
GET http://localhost:8080/api/posts
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

### Step 4: 작성자만 수정 가능하도록 개선
- PostService에서 현재 사용자와 작성자 비교
- 다르면 예외 발생

---

## 🎓 다음 단계로

### 이 단계에서 배운 것
- ✅ Spring Security 설정
- ✅ JWT 토큰 생성/검증
- ✅ 회원가입/로그인 구현
- ✅ 비밀번호 암호화
- ✅ 인증 필터 구현

### 다음 단계: Step 5 - 마이크로서비스 전환

이제 **모놀리식 애플리케이션을 여러 개의 마이크로서비스로 분리**합니다!

---

**준비되셨나요? Step 5로 넘어가서 마이크로서비스 아키텍처를 배워봅시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_05_마이크로서비스_전환_1.md
```

