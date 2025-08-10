package com.example.apigateway

import org.slf4j.LoggerFactory
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.web.cors.CorsConfiguration
import org.springframework.web.cors.reactive.CorsWebFilter
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource
import org.springframework.cloud.gateway.route.RouteLocator
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder
import org.springframework.web.server.ServerWebExchange
import org.springframework.cloud.gateway.filter.GlobalFilter
import reactor.core.publisher.Mono

@SpringBootApplication
class ApiGatewayApplication {
    private val logger = LoggerFactory.getLogger(ApiGatewayApplication::class.java)

    @Bean
    fun corsFilter(): CorsWebFilter {
        val config = CorsConfiguration()
        config.allowCredentials = true
        config.allowedOriginPatterns = listOf("*")
        config.allowedHeaders = listOf("*")
        config.allowedMethods = listOf("GET", "POST", "PUT", "DELETE", "OPTIONS")

        val source = UrlBasedCorsConfigurationSource()
        source.registerCorsConfiguration("/**", config)

        return CorsWebFilter(source)
    }

    @Bean
    fun loggingFilter() = GlobalFilter { exchange: ServerWebExchange, chain ->
        logger.info("Path requested: ${exchange.request.path}")
        logger.info("Method: ${exchange.request.method}")
        logger.info("Headers: ${exchange.request.headers}")
        logger.info("Query params: ${exchange.request.queryParams}")
        
        chain.filter(exchange).then(Mono.fromRunnable {
            logger.info("Response status: ${exchange.response.statusCode}")
        })
    }

    @Bean
    fun customRoutes(builder: RouteLocatorBuilder): RouteLocator = builder.routes()
        .route("upload-service") { r ->
            r.path("/api/audio/upload/**")
                .filters { f ->
                    f.filter { exchange, chain ->
                        logger.info("Routing to upload-service: ${exchange.request.path}")
                        chain.filter(exchange)
                    }
                }
                .uri("http://localhost:8081")
        }
        .route("transcription-service") { r ->
            r.path("/transcript/**")
                .filters { f ->
                    f.filter { exchange, chain ->
                        logger.info("Routing to transcription-service: ${exchange.request.path}")
                        chain.filter(exchange)
                    }
                }
                .uri("http://localhost:8082")
        }
        .route("transcription-api") {
            it.path("/api/transcript/**")
                .filters { f ->
                    f.filter { exchange, chain ->
                        logger.info("Routing to transcription-api: ${exchange.request.path}")
                        chain.filter(exchange)
                    }
                }
                .uri("http://localhost:8082")
        }
        .build()
}

fun main(args: Array<String>) {
    runApplication<ApiGatewayApplication>(*args)
}