# Step 10: 최종 프로젝트 완성

> **목표**: 프론트엔드 연동, CI/CD 파이프라인 구축, 실제 배포까지 경험한다.

---

## 🎯 이 단계를 배우는 이유

### 지금까지의 여정

```
Step 1-2: 기본 CRUD API 개발
Step 3-4: 실무 기능 추가 (페이징, 검색, 인증)
Step 5-7: 마이크로서비스로 전환
Step 8-9: 테스트, 배포, 모니터링

이제 마지막: 프론트엔드 연동 + 자동 배포
```

### 풀스택 개발자로!

```
백엔드만 개발 → API만 제공
풀스택 개발   → 완전한 서비스 제공
```

---

## 💡 핵심 개념

### 1. 프론트엔드 연동

#### CORS 설정

백엔드와 프론트엔드가 다른 포트에서 실행되므로 CORS 설정 필요

```
Frontend: http://localhost:3000
Backend:  http://localhost:8080

→ CORS 정책으로 기본 차단
→ 백엔드에서 허용 설정 필요
```

#### JWT 인증 흐름

```
1. 로그인 → 토큰 받음
2. localStorage에 저장
3. 매 요청마다 Authorization 헤더에 포함
4. 백엔드에서 토큰 검증
```

---

### 2. CI/CD (Continuous Integration/Deployment)

#### 전통적인 배포

```
1. 코드 작성
2. 수동 테스트
3. 수동 빌드
4. 서버에 접속
5. 수동 배포
6. 수동 재시작

→ 시간 많이 걸림, 실수 가능
```

#### CI/CD 파이프라인

```
1. Git Push
   ↓ (자동)
2. 테스트 실행
   ↓ (통과 시)
3. Docker 이미지 빌드
   ↓ (자동)
4. 배포
   ↓ (자동)
5. 재시작

→ 5분 안에 자동 배포
```

**프론트엔드 비유**: Vercel, Netlify 자동 배포
```
Git Push → Vercel이 자동으로 빌드 & 배포
```

---

## 🛠️ 최소 구현 코드

### 1. CORS 설정 (API Gateway)

```java
// com/project/gateway/config/CorsConfig.java

package com.project.gateway.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

@Configuration
public class CorsConfig {
    
    @Bean
    public CorsWebFilter corsWebFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOrigin("http://localhost:3000");  // React 앱
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        
        return new CorsWebFilter(source);
    }
}
```

---

### 2. React 프론트엔드 (기본 구조)

#### 프로젝트 생성

```bash
npx create-react-app board-frontend
cd board-frontend
npm install axios react-router-dom
```

#### API 클라이언트 설정

```javascript
// src/api/apiClient.js

import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json'
    }
});

// 요청 인터셉터: 토큰 자동 추가
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// 응답 인터셉터: 401 에러 시 로그인 페이지로
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default apiClient;
```

#### 로그인 컴포넌트

```javascript
// src/pages/Login.js

import React, { useState } from 'react';
import apiClient from '../api/apiClient';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        
        try {
            const response = await apiClient.post('/user-service/api/auth/login', {
                email,
                password
            });
            
            const { token } = response.data;
            localStorage.setItem('token', token);
            
            // 로그인 성공
            window.location.href = '/posts';
        } catch (error) {
            alert('로그인 실패');
        }
    };

    return (
        <div>
            <h2>로그인</h2>
            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="이메일"
                />
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="비밀번호"
                />
                <button type="submit">로그인</button>
            </form>
        </div>
    );
}

export default Login;
```

#### 게시글 목록 컴포넌트

```javascript
// src/pages/PostList.js

import React, { useEffect, useState } from 'react';
import apiClient from '../api/apiClient';

function PostList() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPosts();
    }, []);

    const fetchPosts = async () => {
        try {
            const response = await apiClient.get('/post-service/api/posts');
            setPosts(response.data.content);
        } catch (error) {
            console.error('게시글 조회 실패', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>로딩 중...</div>;

    return (
        <div>
            <h2>게시글 목록</h2>
            <ul>
                {posts.map(post => (
                    <li key={post.id}>
                        <h3>{post.title}</h3>
                        <p>{post.content}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default PostList;
```

---

### 3. GitHub Actions CI/CD

#### .github/workflows/deploy.yml

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Run Tests
        run: ./gradlew test

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and Push User Service
        run: |
          cd user-service
          docker build -t myusername/user-service:${{ github.sha }} .
          docker push myusername/user-service:${{ github.sha }}
      
      - name: Build and Push Post Service
        run: |
          cd post-service
          docker build -t myusername/post-service:${{ github.sha }} .
          docker push myusername/post-service:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            docker pull myusername/user-service:${{ github.sha }}
            docker pull myusername/post-service:${{ github.sha }}
            docker-compose down
            docker-compose up -d
```

---

### 4. 환경별 설정 관리

#### application-dev.yml (개발)

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
  
  jpa:
    hibernate:
      ddl-auto: create

logging:
  level:
    root: DEBUG
```

#### application-prod.yml (운영)

```yaml
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false

logging:
  level:
    root: INFO
```

#### 환경 변수 설정

```bash
# .env 파일
DB_URL=jdbc:mariadb://db:3306/boarddb
DB_USERNAME=board_user
DB_PASSWORD=secure_password
JWT_SECRET=your-production-secret-key
```

---

## 📝 실습 가이드

### Step 1: CORS 설정
1. API Gateway에 CORS 설정 추가
2. 프론트엔드에서 API 호출 테스트

### Step 2: React 앱 개발
1. `create-react-app`으로 프로젝트 생성
2. API 클라이언트 설정
3. 로그인, 게시글 목록 페이지 개발
4. `npm start`로 실행 (http://localhost:3000)

### Step 3: 전체 시스템 테스트
```
1. 백엔드 서비스 모두 실행
   - Eureka Server
   - API Gateway
   - User Service
   - Post Service

2. 프론트엔드 실행
   - npm start

3. 통합 테스트
   - 로그인
   - 게시글 조회/작성/수정/삭제
```

### Step 4: CI/CD 설정
1. GitHub Repository 생성
2. Docker Hub 계정 생성
3. `.github/workflows/deploy.yml` 추가
4. Git Push → 자동 배포 확인

---

## 🎓 프로젝트 완성!

### 축하합니다! 🎉

10단계를 모두 완료했습니다. 이제 다음을 할 수 있습니다:

#### 기술 역량
- ✅ 스프링부트 기본 개념 이해
- ✅ CRUD API 개발
- ✅ Spring Security, JWT 인증
- ✅ 마이크로서비스 아키텍처 설계
- ✅ API Gateway, Service Discovery
- ✅ 이벤트 기반 아키텍처 (Kafka)
- ✅ Docker, Kubernetes 배포
- ✅ 모니터링, 성능 최적화
- ✅ 프론트엔드 연동
- ✅ CI/CD 파이프라인 구축

#### 실무 준비
- ✅ 백엔드 API 혼자서 개발 가능
- ✅ 마이크로서비스 시스템 설계 가능
- ✅ 풀스택 프로젝트 완성 가능
- ✅ 포트폴리오 제출 가능

---

## 🚀 다음 단계

### 1. 포트폴리오 정리
```
README.md 작성:
- 프로젝트 소개
- 기술 스택
- 아키텍처 다이어그램
- 주요 기능
- API 문서 링크 (Swagger)
- 실행 방법
```

### 2. 추가 기능 구현 (선택)
- 실시간 알림 (WebSocket)
- 파일 업로드 (AWS S3)
- 소셜 로그인 (OAuth 2.0)
- 이메일 인증
- 관리자 페이지

### 3. 기술 블로그 작성
- 학습 과정 정리
- 트러블슈팅 경험 공유
- 기술 선택 이유 설명

### 4. 오픈소스 기여
- Spring Framework
- Spring Cloud
- 관련 라이브러리

---

## 📚 추천 학습 자료

### 책
- **"스프링 부트와 AWS로 혼자 구현하는 웹 서비스"** - 이동욱
- **"마이크로서비스 패턴"** - Chris Richardson
- **"클린 코드"** - Robert C. Martin

### 온라인 강의
- 인프런: "스프링 완전 정복 로드맵"
- Udemy: "Microservices with Spring Boot and Spring Cloud"

### 공식 문서
- Spring Boot Reference
- Spring Cloud Documentation
- Kubernetes Documentation

---

## 💼 취업 준비

### 이력서 작성
```
[프로젝트]
마이크로서비스 기반 게시판 시스템

[기술 스택]
Backend: Spring Boot, Spring Cloud, JPA
Database: MariaDB, Redis
Infra: Docker, Kubernetes
Message: Kafka
Monitoring: Prometheus, Grafana

[주요 성과]
- 모놀리식 → 마이크로서비스 전환
- N+1 문제 해결로 조회 성능 80% 향상
- CI/CD 파이프라인 구축로 배포 시간 90% 단축
- Redis 캐싱 적용으로 응답 속도 50% 개선
```

### 면접 준비
- "왜 마이크로서비스로 전환했나요?"
- "N+1 문제를 어떻게 해결했나요?"
- "Circuit Breaker는 왜 사용했나요?"
- "트랜잭션 관리는 어떻게 했나요?"

---

## 🎯 마무리

### 여러분은 이제...

1. **백엔드 개발자**로서 실무에 투입될 수 있습니다
2. **마이크로서비스 아키텍처**를 설계하고 구현할 수 있습니다
3. **풀스택 개발자**로서 완전한 서비스를 만들 수 있습니다
4. **지속적으로 학습**할 수 있는 기반을 다졌습니다

### 학습은 계속됩니다

기술은 계속 발전합니다. 하지만 이제 여러분은 **스스로 학습할 수 있는 능력**을 갖췄습니다.

**화이팅! 여러분의 개발 여정을 응원합니다! 🚀**

---

## 📞 질문이나 피드백

- 문서 개선 제안
- 버그 리포트
- 추가 기능 요청

언제든 환영합니다!

**감사합니다!**

