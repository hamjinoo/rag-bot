# Step 8: 테스트 및 배포

> **목표**: 테스트 자동화, Docker 컨테이너화, Kubernetes 배포를 경험한다.

---

## 🎯 이 단계를 배우는 이유

### 테스트 없이 배포하면?

```
코드 수정 → 수동 테스트 → 배포
              ↓
         놓친 버그 발견
              ↓
         긴급 패치
              ↓
         또 다른 버그...
```

### 테스트 자동화의 장점

```
코드 수정 → 자동 테스트 실행 → 배포
              ↓ 통과 시에만
           안심하고 배포
```

### 프론트엔드 비유

```javascript
// Jest로 컴포넌트 테스트
test('버튼 클릭 시 카운터 증가', () => {
    render(<Counter />);
    fireEvent.click(screen.getByText('증가'));
    expect(screen.getByText('1')).toBeInTheDocument();
});

// JUnit으로 서비스 테스트
@Test
void 게시글_생성_성공() {
    Post post = postService.create(new Post("제목", "내용"));
    assertThat(post.getId()).isNotNull();
}
```

---

## 💡 핵심 개념

### 1. 테스트 피라미드

```
        /\
       /E2E\        ← 소수 (느림, 비싸지만 현실적)
      /------\
     /통합 테스트\    ← 중간 (API 테스트)
    /----------\
   /  단위 테스트  \  ← 다수 (빠름, 저렴)
  /--------------\
```

#### 단위 테스트 (Unit Test)
- 하나의 메서드/클래스만 테스트
- 빠름, 많이 작성
- 예: `PostService.create()` 테스트

#### 통합 테스트 (Integration Test)
- 여러 계층 통합 테스트
- DB, 외부 API 포함
- 예: Controller → Service → Repository

#### E2E 테스트 (End-to-End Test)
- 실제 사용자 시나리오
- 브라우저 자동화 (Selenium)
- 가장 느림, 소수만 작성

---

### 2. Docker

#### 가상 머신 vs 컨테이너

```
가상 머신 (VM):
[App A] [App B]
[OS A]  [OS B]  ← 각각 OS 포함 (무거움)
[Hypervisor]
[Host OS]

컨테이너 (Docker):
[App A] [App B]
[Docker Engine]  ← OS 공유 (가벼움)
[Host OS]
```

#### 프론트엔드 비유

```
npm install → 로컬 환경에 따라 다를 수 있음
Docker → 어디서나 똑같이 실행
```

---

### 3. Kubernetes (K8s)

#### Docker vs Kubernetes

```
Docker: 컨테이너 실행
Kubernetes: 여러 컨테이너 관리/오케스트레이션

예:
- User Service 컨테이너 3개 실행
- 하나 죽으면 자동 재시작
- 로드 밸런싱
- 자동 스케일링
```

---

## 🛠️ 최소 구현 코드

### 1. 단위 테스트 (JUnit + Mockito)

#### 의존성 (이미 포함됨)
```gradle
dependencies {
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

#### PostServiceTest.java
```java
// src/test/java/com/project/post/service/PostServiceTest.java

package com.project.post.service;

import com.project.post.model.Post;
import com.project.post.repository.PostRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PostServiceTest {
    
    @Mock  // 가짜 객체
    private PostRepository postRepository;
    
    @InjectMocks  // postRepository를 주입받는 실제 객체
    private PostService postService;
    
    @Test
    void 게시글_생성_성공() {
        // Given (준비)
        Post post = new Post();
        post.setTitle("테스트 제목");
        post.setContent("테스트 내용");
        
        when(postRepository.save(any(Post.class)))
            .thenReturn(post);
        
        // When (실행)
        Post savedPost = postService.create(post);
        
        // Then (검증)
        assertThat(savedPost).isNotNull();
        assertThat(savedPost.getTitle()).isEqualTo("테스트 제목");
        verify(postRepository, times(1)).save(any(Post.class));
    }
    
    @Test
    void 게시글_조회_실패() {
        // Given
        when(postRepository.findById(1L))
            .thenReturn(Optional.empty());
        
        // When & Then
        assertThatThrownBy(() -> postService.findById(1L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessage("게시글을 찾을 수 없습니다.");
    }
}
```

**실행**:
```bash
./gradlew test
```

---

### 2. 통합 테스트

#### PostControllerIntegrationTest.java
```java
// src/test/java/com/project/post/controller/PostControllerIntegrationTest.java

package com.project.post.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.post.model.Post;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest  // 스프링 부트 전체 실행
@AutoConfigureMockMvc  // MockMvc 자동 설정
@Transactional  // 테스트 후 롤백
class PostControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;  // HTTP 요청 시뮬레이션
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Test
    void 게시글_생성_API_테스트() throws Exception {
        // Given
        Post post = new Post();
        post.setTitle("통합 테스트");
        post.setContent("내용");
        
        // When & Then
        mockMvc.perform(post("/api/posts")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(post)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.title").value("통합 테스트"));
    }
    
    @Test
    void 존재하지_않는_게시글_조회() throws Exception {
        mockMvc.perform(get("/api/posts/999"))
            .andExpect(status().isNotFound());
    }
}
```

---

### 3. Docker 컨테이너화

#### Dockerfile 생성 (각 서비스마다)
```dockerfile
# Dockerfile (user-service/)

# 1단계: 빌드
FROM gradle:8.5-jdk17 AS build
WORKDIR /app
COPY . .
RUN gradle clean build -x test

# 2단계: 실행
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
```

#### 이미지 빌드
```bash
# User Service 이미지 빌드
cd user-service
docker build -t user-service:1.0 .

# Post Service 이미지 빌드
cd ../post-service
docker build -t post-service:1.0 .
```

#### 컨테이너 실행
```bash
docker run -d -p 8081:8081 --name user-service user-service:1.0
docker run -d -p 8082:8082 --name post-service post-service:1.0
```

---

### 4. Docker Compose (여러 서비스 한 번에)

#### docker-compose.yml
```yaml
version: '3.8'

services:
  eureka-server:
    build: ./eureka-server
    ports:
      - "8761:8761"
    networks:
      - board-network

  user-service:
    build: ./user-service
    ports:
      - "8081:8081"
    environment:
      EUREKA_CLIENT_SERVICEURL_DEFAULTZONE: http://eureka-server:8761/eureka/
    depends_on:
      - eureka-server
    networks:
      - board-network

  post-service:
    build: ./post-service
    ports:
      - "8082:8082"
    environment:
      EUREKA_CLIENT_SERVICEURL_DEFAULTZONE: http://eureka-server:8761/eureka/
    depends_on:
      - eureka-server
    networks:
      - board-network

  api-gateway:
    build: ./api-gateway
    ports:
      - "8080:8080"
    environment:
      EUREKA_CLIENT_SERVICEURL_DEFAULTZONE: http://eureka-server:8761/eureka/
    depends_on:
      - eureka-server
    networks:
      - board-network

networks:
  board-network:
    driver: bridge
```

**실행**:
```bash
docker-compose up -d
```

---

### 5. Kubernetes 기초

#### Deployment (user-service-deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3  # 3개 인스턴스
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:1.0
        ports:
        - containerPort: 8081
        env:
        - name: EUREKA_CLIENT_SERVICEURL_DEFAULTZONE
          value: "http://eureka-server:8761/eureka/"
```

#### Service (user-service-service.yaml)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  type: LoadBalancer
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 8081
```

**배포**:
```bash
# Deployment 생성
kubectl apply -f user-service-deployment.yaml

# Service 생성
kubectl apply -f user-service-service.yaml

# 확인
kubectl get pods
kubectl get services
```

---

## 📝 실습 가이드

### Step 1: 단위 테스트 작성
1. `PostServiceTest.java` 생성
2. `./gradlew test` 실행
3. 테스트 결과 확인

### Step 2: 통합 테스트 작성
1. `PostControllerIntegrationTest.java` 생성
2. 실행 및 확인

### Step 3: Docker 빌드
1. Dockerfile 작성
2. `docker build` 실행
3. `docker run` 으로 컨테이너 실행

### Step 4: Docker Compose
1. `docker-compose.yml` 작성
2. `docker-compose up` 실행
3. 모든 서비스 접근 테스트

### Step 5: Kubernetes (선택)
- Minikube 설치
- Deployment, Service YAML 작성
- `kubectl apply` 배포

---

## 🎓 다음 단계로

### 이 단계에서 배운 것
- ✅ 단위/통합 테스트 (JUnit, MockMvc)
- ✅ Docker 컨테이너화
- ✅ Docker Compose
- ✅ Kubernetes 기초

### 다음 단계: Step 9 - 모니터링 및 최적화

**Step 9에서 배울 것**:
1. **로깅**: ELK 스택, Logback
2. **성능 최적화**: N+1 문제, 캐싱
3. **모니터링**: Prometheus, Grafana

---

**준비되셨나요? Step 9로 넘어가서 모니터링과 최적화를 배워봅시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_09_모니터링_최적화.md
```

